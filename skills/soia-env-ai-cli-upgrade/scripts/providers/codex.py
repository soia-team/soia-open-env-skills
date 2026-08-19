"""Codex — native `codex update`（内部自检 native/brew-cask/npm）。"""
from ._common import Provider, _run, print_result


class CodexProvider(Provider):
    name = "codex"
    command = "codex"
    registry_package = "@openai/codex"

    def upgrade(self, binary, old_version):
        if _run([binary, "update"]).returncode != 0:
            print_result(self.name, self.command, old_version, old_version, "FAILED",
                         f"{self.command} update failed; path={binary}")
            return False
        return True
