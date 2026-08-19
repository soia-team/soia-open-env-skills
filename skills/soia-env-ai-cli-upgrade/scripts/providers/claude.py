"""Claude Code — 按安装方法升级：native/unknown → update；brew → cask 逻辑
（含 CLAUDE_CHANNEL=latest 通道迁移）；npm → registry 重装；desktop → MANUAL。"""
from ._common import (Provider, _run, print_result, detect_claude_method,
                      detect_brew_claude_cask, migrate_brew_claude_to_latest,
                      reinstall_from_registry, claude_channel)


class ClaudeProvider(Provider):
    name = "claude"
    command = "claude"
    registry_package = "@anthropic-ai/claude-code"

    def upgrade(self, binary, old_version):
        install_method = detect_claude_method(binary)
        if install_method in ("native", "unknown"):
            if _run([binary, "update"]).returncode != 0:
                print_result(self.name, self.command, old_version, old_version, "FAILED",
                             f"claude update failed; path={binary}")
                return False
            return True
        if install_method == "brew":
            cask = detect_brew_claude_cask()
            if not cask:
                print_result(self.name, self.command, old_version, old_version, "FAILED",
                             f"brew cask detection failed; path={binary}")
                return False
            if cask == "claude-code" and claude_channel == "latest":
                if not migrate_brew_claude_to_latest(cask):
                    print_result(self.name, self.command, old_version, old_version, "FAILED",
                                 "Claude channel switch to claude-code@latest failed; "
                                 "stable cask restore attempted")
                    return False
                return True
            if _run(["brew", "upgrade", "--cask", cask]).returncode != 0:
                print_result(self.name, self.command, old_version, old_version, "FAILED",
                             f"brew upgrade --cask {cask} failed; path={binary}")
                return False
            return True
        if install_method == "npm":
            registry_rc = reinstall_from_registry(self.registry_package)
            if registry_rc == "no-npm":
                print_result(self.name, self.command, old_version, old_version, "FAILED",
                             f"npm not found for {self.registry_package}")
                return False
            if registry_rc == "failed":
                print_result(self.name, self.command, old_version, old_version, "FAILED",
                             f"npm install -g {self.registry_package} failed")
                return False
            return True
        if install_method == "desktop":
            print_result(self.name, self.command, old_version, old_version, "MANUAL",
                         f"Desktop-managed; update via Claude Desktop app; path={binary}")
            return False
        print_result(self.name, self.command, old_version, old_version, "MANUAL",
                     "no upgrader config")
        return False
