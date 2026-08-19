"""DeepSeek Harness (dsh) — 官方 scoped 包 @deepseek-ai/dsh 走 npm 渠道；
裸名 `dsh` 是被占用的无关老包，勿用。native 无已知渠道报 MANUAL。"""
from ._common import ChannelProvider


class DshProvider(ChannelProvider):
    name = "dsh"
    command = "dsh"
    registry_package = "@deepseek-ai/dsh"
    native_manual = "no known channel (official install is npm @deepseek-ai/dsh)"
