"""AI CLI 升级器注册表：TOOL → Provider 实例，以及默认批次顺序。"""
from .codex import CodexProvider
from .claude import ClaudeProvider
from .agy import AgyProvider
from .gemini import GeminiProvider
from .qwen import QwenProvider
from .mmx import MmxProvider
from .kimi import KimiProvider
from .opencode import OpenCodeProvider
from .qodercli import QoderCliProvider
from .cursor import CursorProvider
from .deepcode import DeepCodeProvider
from .dsh import DshProvider
from .pi import PiProvider

PROVIDERS = {
    p.name: p for p in (
        CodexProvider(), ClaudeProvider(), AgyProvider(), GeminiProvider(),
        QwenProvider(), MmxProvider(), KimiProvider(), OpenCodeProvider(),
        QoderCliProvider(), CursorProvider(), DeepCodeProvider(), DshProvider(),
        PiProvider(),
    )
}

DEFAULT_TOOLS = ["codex", "claude", "agy", "kimi", "mmx", "qwen",
                 "opencode", "qodercli", "cursor", "deepcode", "dsh", "pi"]
