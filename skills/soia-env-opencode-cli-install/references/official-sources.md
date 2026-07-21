# OpenCode CLI 官方来源

核对日期：2026-07-21。

- [OpenCode 安装文档](https://opencode.ai/docs)：官方独立安装、npm、Homebrew 和首次运行说明。
- [OpenCode 配置文档](https://opencode.ai/docs/config/)：全局配置、项目配置和环境变量。
- [OpenCode CLI 文档](https://opencode.ai/docs/cli/)：`opencode` 命令与 `upgrade` 用法。
- [官方 GitHub 仓库](https://github.com/anomalyco/opencode)：发布版本和安装来源。
- [npm 官方包](https://www.npmjs.com/package/opencode-ai)：npm 渠道包名与发布版本。

已核对事实：命令名是 `opencode`；npm 包名是 `opencode-ai`；显式更新命令是 `opencode upgrade`，并可指定来源；默认全局配置位于 `~/.config/opencode/opencode.json`，可由 `OPENCODE_CONFIG` 或 `OPENCODE_CONFIG_DIR` 覆盖；供应商认证由 `opencode auth login` 管理，凭据文件位于 `~/.local/share/opencode/auth.json`，可用 `opencode auth list` 检查。产品可在启动时检查并下载更新；技能只报告 `autoupdate` 设置，不自行改成 `false` 或 `notify`。

官方独立安装脚本必须先保存到每次运行独立的系统临时目录，检查 HTTPS 来源、脚本内容和安装目标，再执行本地副本；不得把网络响应直接交给 shell。结束后清理临时文件。
