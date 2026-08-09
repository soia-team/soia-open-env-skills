# Standard Workflow（命令变体）与回执核对清单

## 命令变体

仓内运行：

```bash
# 只审计版本
DRY_RUN=1 python3 skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py

# 升级全部受支持工具
python3 skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py

# 升级消费者安全子集
TOOLS="codex,claude,agy" \
  python3 skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py

# 单独授权换通道后，把 Homebrew Claude 迁到 @latest
CLAUDE_CHANNEL=latest TOOLS="claude" \
  python3 skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py

# 确认属受支持的非消费者通道后，才升级 Gemini CLI
TOOLS="gemini" \
  python3 skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py

# 显式授权安装缺失的 agy（不含登录）
AGY_INSTALL=1 TOOLS="agy" \
  python3 skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py
```

已安装技能运行：

```bash
DRY_RUN=1 python3 ~/.agents/skills/soia-env-ai-cli-upgrade/scripts/upgrade_ai_clis.py
```

脚本每次写一个带时间戳的日志文件并打印七列状态表（列语义见
[configuration.md](configuration.md)）。

## Output Checklist（最终回复前核对）

- 说明本次是 dry-run 还是真实升级。
- 附日志文件路径。
- 逐工具汇总状态。
- 点名所有 `FAILED`、`MANUAL` 或需要交互登录的阻塞项。
- Homebrew Claude 报告实际 cask 通道；`ALREADY_LATEST` 只代表「保留通道内已最新」，
  不证明其他已授权通道没有更新版本。
- 脚本非零退出视为至少一行真实 `FAILED`；脚本仍会处理完其余选中工具再返回失败。
- 除非用户完成了显式 PTY 登录流程，声明「未检查认证状态」；等待期间用
  `blocked_user_action`。
- 请求了模型发现时，报告 `model_source=runtime_account_scoped` 与 `agy models`
  返回的显示名；不由该输出杜撰稳定模型 id、别名、默认值或套餐资格。
- 跑了真实升级时，尽可能报告旧/新版本。
