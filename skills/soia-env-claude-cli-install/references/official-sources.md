# Claude Code CLI 官方来源

核对日期：2026-07-21。

- [Claude Code 快速开始](https://docs.anthropic.com/en/docs/claude-code/getting-started)：官方安装入口、启动和首次登录流程。
- [Claude Code 设置](https://docs.anthropic.com/en/docs/claude-code/settings)：用户配置目录、环境变量和自动更新设置。
- [Claude Code CLI 参考](https://docs.anthropic.com/en/docs/claude-code/cli-reference)：`claude` 命令与无害验证参数。
- [npm 官方包](https://www.npmjs.com/package/@anthropic-ai/claude-code)：npm 渠道的包名与发布版本。

已核对事实：命令名是 `claude`；npm 包名是 `@anthropic-ai/claude-code`，当前包声明 Node.js 22 或更高版本；官方独立安装与 npm 安装是不同来源；`claude update` 用于受支持安装的显式更新；`claude doctor` 可诊断安装与自动更新状态。Claude Code 自身可能启用自动更新，技能只报告该状态，除非客户明确要求，否则不修改 `autoUpdates` 或 `DISABLE_AUTOUPDATER`。

供应商页面可能给出网络脚本的一行安装示例。本技能必须先把脚本下载到每次运行独立的系统临时目录，核对 HTTPS 主机、文件类型和脚本内容，展示将执行的来源与目标，再按权限边界执行；禁止把远程响应直接送入 shell。成功或失败都删除临时文件。
