# Kimi Code CLI 官方来源

核对日期：2026-07-21。

- [Kimi Code CLI 快速开始](https://www.kimi.com/code/docs/kimi-code-cli/guides/getting-started)：官方安装、登录、启动和系统要求。
- [Kimi Code CLI 配置](https://www.kimi.com/code/docs/kimi-code-cli/configuration)：配置目录、配置文件与环境变量。
- [Kimi Code CLI 命令](https://www.kimi.com/code/docs/kimi-code-cli/reference/commands)：登录、更新与无害验证命令。
- [官方安装脚本](https://code.kimi.com/kimi-code/install.sh)：macOS/Linux 独立安装入口。
- [npm 官方包](https://www.npmjs.com/package/@moonshot-ai/kimi-code)：npm 渠道包名和发布版本。

已核对事实：命令名是 `kimi`；npm 包名是 `@moonshot-ai/kimi-code`，当前包声明 Node.js 22.19 或更高版本；官方独立安装不应被错误地阻塞在 Node.js 检查；登录使用 `kimi login` 或交互界面的 `/login`；显式更新可用 `kimi upgrade`/`kimi update`；默认配置和状态目录是 `~/.kimi-code`，可由 `KIMI_CODE_HOME` 覆盖。产品可能后台检查更新，技能只报告 `KIMI_CODE_NO_AUTO_UPDATE` 或对应 TUI 设置，不自行修改。

官方安装脚本必须先保存到独立临时目录并检查来源、内容和安装目标，再执行本地副本；不得直接执行网络响应。成功或失败都清理临时文件。
