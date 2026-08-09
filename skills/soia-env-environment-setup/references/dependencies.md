# 依赖与安装（完整表）

| 依赖 | 类型 | 处理方式 |
|---|---|---|
| `soia-env-network-diagnose` | 前置技能 | 网络侧先检查 DNS/HTTPS/下载源，本机侧盘点运行时并推导各 AI CLI 可安装性；缺少时做最小检查 |
| `soia-env-node-install` | 按目标启用 | Codex 或 Node 项目需要时调用 |
| `soia-env-python-install` | 按目标启用 | Python 项目或脚本需要时调用 |
| `soia-env-codex-install` | 按目标启用 | 客户明确要使用 Codex 时调用 |
| `soia-env-claude-cli-install` | 按目标启用 | 客户明确要使用 Claude Code CLI 时调用 |
| `soia-env-qoder-cli-install` | 按目标启用 | 客户明确要使用 Qoder CLI 时调用 |
| `soia-env-antigravity-cli-install` | 按目标启用 | 客户要安装 `agy` 或从 Gemini CLI 迁移时调用 |
| `soia-env-opencode-cli-install` | 按目标启用 | 客户明确要使用 OpenCode CLI 时调用 |
| `soia-env-kimi-cli-install` | 按目标启用 | 客户明确要使用 Kimi Code CLI 时调用 |
| `soia-env-deepcode-cli-install` | 按目标启用 | 客户确认目标是 `lessweb/deepcode-cli` 时调用；先准备 Node.js 22+ |
| `soia-env-codex-setup-support` | 按目标启用 | 同时涉及桌面版、CLI 或 Codex 故障排查时调用 |
| `soia-env-workbuddy-install` | 按目标启用 | 客户明确要使用 WorkBuddy 时调用 |
| `soia-env-storage-cleanup` | 按目标启用 | 客户要求统计或清理 SOIA 受管空间时调用；删除必须先展示计划并重新取得明确授权 |
| `soia-env-open-skills-install` | 按目标启用 | 环境就绪后客户要装 SOIA 技能生态时调用；接管插件市场接入与域插件安装，不由本技能执行 |
| `soia-open-skills` | 方法邻居 | 完成环境摘要后再衔接 PKM/云盘技能，不复制其文件 |
| `soia-private-skills` | 私有方法邻居 | 只有已安装且任务需要时才提示，不自动安装 |

各专门技能的官方来源和版本事实见其 `references/`。本技能不读取私有凭据文件。
