"""MiniMax CLI (mmx) — native `mmx update`（内部封装 npm）。"""
from ._common import Provider, _run, print_result


class MmxProvider(Provider):
    name = "mmx"
    command = "mmx"
    registry_package = "mmx-cli"

    def upgrade(self, binary, old_version):
        if _run([binary, "update"]).returncode != 0:
            print_result(self.name, self.command, old_version, old_version, "FAILED",
                         f"{self.command} update failed; path={binary}")
            return False
        return True
