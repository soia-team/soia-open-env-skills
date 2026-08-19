"""Cursor — 仅版本审计；升级需用户自设 CURSOR_UPGRADE_CMD（视为用户提供代码）。"""
import os

from ._common import Provider, _run, print_result, IS_WINDOWS


class CursorProvider(Provider):
    name = "cursor"
    command = "cursor"
    registry_package = ""

    def upgrade(self, binary, old_version):
        cursor_cmd = os.environ.get("CURSOR_UPGRADE_CMD", "")
        if not cursor_cmd:
            print_result(self.name, self.command, old_version, old_version, "MANUAL",
                         "no default updater; set CURSOR_UPGRADE_CMD")
            return False
        shell_argv = (["cmd", "/c", cursor_cmd] if IS_WINDOWS
                      else ["bash", "-lc", cursor_cmd])
        if _run(shell_argv).returncode != 0:
            print_result(self.name, self.command, old_version, old_version, "FAILED",
                         "CURSOR_UPGRADE_CMD failed")
            return False
        return True
