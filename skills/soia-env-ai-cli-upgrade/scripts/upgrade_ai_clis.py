#!/usr/bin/env python3
# @created_by  claude-fable-5
# @created_at  2026-08-08 14:10:00
# @version     2.3.1
# @description Audit and safely upgrade supported AI/developer CLIs (Python engine).
# @changelog   dsh: DSH_TRACK 轨道对齐（latest/next）+ CLI 与 ~/.dsh/profiles
#              客户端包版本一致性提示（bootstrap 接口不匹配防回归）。
#              Previously: split monolithic engine into entry + providers/ package
#              (one file per AI CLI); behavior unchanged, contract tests still lock
#              the CLI. Previously: add DeepSeek Harness (dsh) support via npm
#              registry package @deepseek-ai/dsh; native installs without a known
#              channel report MANUAL. Previously: security hardening per Tencent
#              Yunding scan (2026-08-08): rename identifiers off the npm
#              secret-token prefix pattern; replace pipe-to-shell suggestion
#              strings with download-review-run wording. Previously:
#              platform-aware paths for native Windows; agy MANUAL on Windows.
#              Previously: port bash engine verbatim; ~/.opencode/bin fallback.
"""AI CLI 升级助手引擎——入口（CLI 调度）。

配置加载、日志、探测与统一收尾在 `providers/_common.py`；每个 AI CLI 的升级
渠道在 `providers/<tool>.py`。对外契约（环境变量、表格列、状态字、退出码、
日志命名与轮转）由仓级契约测试锁定，本重构行为零变化。
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from providers import PROVIDERS, DEFAULT_TOOLS  # noqa: E402
from providers import _common  # noqa: E402


def main():
    _common.print_header()
    selector = os.environ.get("TOOLS") or os.environ.get("NPM_PACKAGES") or ""
    if selector:
        tools = [t.strip() for t in selector.split(",") if t.strip()]
    else:
        tools = DEFAULT_TOOLS
    for tool in tools:
        provider = PROVIDERS.get(tool)
        if provider is None:
            # 未知工具：与旧行为一致——裸 Provider 报 MANUAL no upgrader config
            provider = _common.Provider()
            provider.name, provider.command = tool, tool
        provider.run()
    if _common.had_failure:
        _common.log(f"DONE_WITH_FAILURES. detail log: {_common.log_file}")
        sys.exit(1)
    _common.log(f"DONE. detail log: {_common.log_file}")


if __name__ == "__main__":
    main()
