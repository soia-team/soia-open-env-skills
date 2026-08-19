"""Qoder CLI (qodercli) — native `qodercli update`。"""
from ._common import Provider, _run, print_result


class QoderCliProvider(Provider):
    name = "qodercli"
    command = "qodercli"
    registry_package = ""

    def upgrade(self, binary, old_version):
        if _run([binary, "update"]).returncode != 0:
            print_result(self.name, self.command, old_version, old_version, "FAILED",
                         "qodercli update failed")
            return False
        return True
