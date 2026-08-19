"""Antigravity CLI (agy) — native `agy update`；缺失安装由基类 handle_missing
按 AGY_INSTALL=1 授权走官方安装器；PATH 解析特判在统一收尾中完成。"""
from ._common import Provider, _run, print_result


class AgyProvider(Provider):
    name = "agy"
    command = "agy"
    registry_package = ""

    def upgrade(self, binary, old_version):
        if _run([binary, "update"]).returncode != 0:
            print_result(self.name, self.command, old_version, old_version, "FAILED",
                         f"agy update failed; path={binary}")
            return False
        return True
