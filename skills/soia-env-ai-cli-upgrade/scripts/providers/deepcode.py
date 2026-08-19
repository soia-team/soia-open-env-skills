"""DeepCode Agent CLI — 三渠道：brew（理论）/ npm；无已知 native 渠道。"""
from ._common import ChannelProvider


class DeepCodeProvider(ChannelProvider):
    name = "deepcode"
    command = "deepcode"
    registry_package = "@vegamo/deepcode-cli"
