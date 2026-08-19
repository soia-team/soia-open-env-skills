"""OpenCode — 三渠道：brew / npm；native 无法自动升级，MANUAL 引导官方安装器。"""
from ._common import ChannelProvider


class OpenCodeProvider(ChannelProvider):
    name = "opencode"
    command = "opencode"
    registry_package = "opencode-ai"
    native_manual = ("native install; refresh via official installer "
                     "(download from opencode.ai/install, review, then run locally)")
