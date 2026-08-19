"""Kimi Code — 三渠道：brew / npm / native `kimi upgrade`。"""
from ._common import ChannelProvider


class KimiProvider(ChannelProvider):
    name = "kimi"
    command = "kimi"
    registry_package = "@moonshot-ai/kimi-code"
    native_cmd = "upgrade"
