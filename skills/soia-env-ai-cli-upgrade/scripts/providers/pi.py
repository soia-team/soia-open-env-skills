"""Pi (pi-coding-agent) — `pi update --self`（npm 包 @earendil-works/pi-coding-agent）。"""
from ._common import Provider, _run, print_result


class PiProvider(Provider):
    name = "pi"
    command = "pi"
    registry_package = "@earendil-works/pi-coding-agent"

    def upgrade(self, binary, old_version):
        if _run([binary, "update", "--self"]).returncode != 0:
            print_result(self.name, self.command, old_version, old_version, "FAILED",
                         f"pi update --self failed; path={binary}")
            return False
        return True
