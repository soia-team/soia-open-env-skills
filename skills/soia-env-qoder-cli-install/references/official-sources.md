# Qoder CLI 官方来源

核对日期：2026-07-21。

- [Qoder CLI Quick Start](https://docs.qoder.com/en/cli/quick-start)：系统要求、官方安装渠道、`qodercli` 启动与登录。
- [Using Qoder CLI](https://docs.qoder.com/en/cli/using-cli)：交互界面、登录与常用流程。
- [Qoder CLI Command](https://docs.qoder.com/en/cli/command)：命令和参数参考。
- [npm 官方包](https://www.npmjs.com/package/@qoder-ai/qodercli)：npm 渠道包名与发布版本。

已核对事实：命令名是 `qodercli`；npm 包名是 `@qoder-ai/qodercli`，当前包声明 Node.js 20 或更高版本；登录可通过 `qodercli login` 或交互界面的 `/login`；显式更新可用 `qodercli update` 或原包管理器；用户配置位于 `~/.qoder/settings.json`，项目可有 `.qoder/settings.json` 和 `.qoder/settings.local.json`。产品自动更新默认可用，技能只报告设置，不自行修改 `general.enableAutoUpdate`。

官方安装脚本必须先下载到独立临时目录并检查来源、内容和目标，再执行本地临时文件；不得把网络响应直接交给 shell。安装完成或失败都清理临时文件。
