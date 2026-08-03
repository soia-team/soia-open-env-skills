# Pi（pi-coding-agent）上游来源

核对日期：2026-08-03。

- [earendil-works/pi-coding-agent 上游仓库](https://github.com/earendil-works/pi-coding-agent)：项目身份、安装、命令、配置、扩展和技能说明。
- [npm 包](https://www.npmjs.com/package/@earendil-works/pi-coding-agent)：安装包与发布版本。
- [Pi 文档](https://github.com/earendil-works/pi-coding-agent/tree/main/docs)：环境变量、模型、扩展、技能、主题等。

身份边界：本技能中的 Pi 是 `@earendil-works/pi-coding-agent` 开源项目，命令 `pi`。它不是 Qwen、DeepCode 或其他同名工具。若客户给出不同仓库，先停下并重新确认，不安装近似名称包。

已核对事实：npm 包名是 `@earendil-works/pi-coding-agent`；命令是 `pi`；用户配置是 `~/.pi/agent/settings.json`（非秘密的 provider/model/theme），Provider 凭据走环境变量或 `pi auth`；数据目录 `~/.pi/agent/` 含 sessions/skills/extensions/git/npm；CLI 会发现 `~/.agents/skills`、`~/.pi/agent/skills` 和项目 `.pi/skills`、`.agents/skills`；自更新命令 `pi update --self`。真实启动时若缺少凭据，会提示相应 Provider 配置缺失；运行命令可初始化部分运行状态，但不会替客户生成包含凭据的 `settings.json`。
