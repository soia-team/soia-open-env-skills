"""Gemini CLI（非消费者通道）— 三渠道：brew / npm / native `gemini update`。"""
from ._common import ChannelProvider


class GeminiProvider(ChannelProvider):
    name = "gemini"
    command = "gemini"
    registry_package = "@google/gemini-cli"
    native_cmd = "update"
