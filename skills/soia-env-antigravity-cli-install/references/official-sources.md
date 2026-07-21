# Google Antigravity CLI 官方来源

核对日期：2026-07-21。

- [Antigravity CLI hands-on](https://codelabs.developers.google.com/antigravity-cli-hands-on)：Google 官方安装、首次运行和 `agy` 使用流程。
- [Installation & Auth](https://antigravity.google/docs/cli/install)：安装目录、官方安装入口和登录流程。
- [CLI troubleshooting](https://antigravity.google/docs/cli/troubleshooting)：PATH、登录与故障排查。
- [Gemini CLI migration](https://antigravity.google/docs/cli/gcli-migration)：从 Gemini CLI 迁移到 Antigravity CLI 的产品边界。
- [官方安装脚本](https://antigravity.google/cli/install.sh)：macOS/Linux 独立安装入口。

已核对事实：当前命令名是 `agy`；默认用户级二进制目录为 `~/.local/bin`，Windows 默认位于 `%LOCALAPPDATA%\\agy\\bin`；`agy update` 执行显式更新；配置和状态位于 `~/.gemini/antigravity-cli`，全局 MCP 配置位于 `~/.gemini/config/mcp_config.json`。Antigravity CLI 是 Gemini CLI 的后继迁移目标，但不是同一个命令，状态列表不得把 `gemini` 当成 `agy` 已安装。产品包含后台自更新能力；技能只报告 `AGY_CLI_DISABLE_AUTO_UPDATE` 状态，不自行改写。

官方安装脚本使用 Google 的平台清单选择二进制。本技能先下载脚本到独立临时目录，检查 `antigravity.google` 来源、脚本内容和下载目标，再执行本地副本；不得直接执行网络响应。临时脚本和下载文件在成功或失败后都清理。
