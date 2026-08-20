"""DeepSeek Harness (dsh) — 官方 scoped 包 @deepseek-ai/dsh 走 npm 渠道；
裸名 `dsh` 是被占用的无关老包，勿用。native 无已知渠道报 MANUAL。

双版本轨道：`latest`（npm 默认，稳定）与 `next`（预发布）。profiles 客户端包
（~/.dsh/profiles/node_modules/@deepseek-ai/dsh-app-boot）可能与全局 CLI 处于
不同轨道，HTML bootstrap 接口会因此不匹配（rc.7 注入 __DSH_BOOT__，rc.8 改用
window.__ModuleLoader__，启动报 bootstrap facade missing）。`DSH_TRACK` 让升级
轨道与 profiles 对齐；审计时对 CLI 与 profiles 版本做一致性提示。
"""
import json
import os
import sys
from pathlib import Path

from ._common import ChannelProvider, HOME, global_prefix

DSH_TRACKS = ("latest", "next")


def dsh_track():
    """读取 DSH_TRACK（默认 latest）；非法值立即报错退出（与 CLAUDE_CHANNEL 同模式）。"""
    track = os.environ.get("DSH_TRACK", "latest")
    if track not in DSH_TRACKS:
        print(f"invalid DSH_TRACK={track}; expected {' or '.join(DSH_TRACKS)}",
              file=sys.stderr)
        sys.exit(2)
    return track


def _profiles_root():
    return Path(os.environ.get("DSH_PROFILES_DIR") or HOME / ".dsh/profiles")


def profiles_version():
    """~/.dsh/profiles 客户端包版本，以 dsh-app-boot 为锚点；缺失返回空串。"""
    pkg = (_profiles_root() / "node_modules" / "@deepseek-ai"
           / "dsh-app-boot" / "package.json")
    try:
        return json.loads(pkg.read_text(encoding="utf-8")).get("version", "")
    except (OSError, ValueError):
        return ""


class DshProvider(ChannelProvider):
    name = "dsh"
    command = "dsh"
    registry_package = "@deepseek-ai/dsh"
    native_manual = "no known channel (official install is npm @deepseek-ai/dsh)"

    def run(self):
        dsh_track()  # 早期校验非法 DSH_TRACK（dry-run 也生效）
        super().run()

    def _package_spec(self):
        """升级包名：next 轨道限定为 @deepseek-ai/dsh@next，latest 用裸包名。"""
        track = dsh_track()
        return f"{self.registry_package}@{track}" if track != "latest" \
            else self.registry_package

    def upgrade(self, binary, old_version):
        original = self.registry_package
        self.registry_package = self._package_spec()
        try:
            return super().upgrade(binary, old_version)
        finally:
            self.registry_package = original

    def extra_note(self, binary, version=""):
        pv = profiles_version()
        if not pv:
            return ""
        note = f"; profiles={pv}"
        if version and pv != version:
            note += (f"; MISMATCH: profiles={pv} cli={version} — "
                     f"run `npm install -g --prefix {global_prefix} "
                     f"@deepseek-ai/dsh@{dsh_track()}` to align")
        return note
