"""Qwen Code — 三渠道：brew / npm / native `qwen update`。"""
from ._common import ChannelProvider


class QwenProvider(ChannelProvider):
    name = "qwen"
    command = "qwen"
    registry_package = "@qwen-code/qwen-code"
    native_cmd = "update"
