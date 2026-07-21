# Deep Code CLI 上游来源

核对日期：2026-07-21。

- [lessweb/deepcode-cli 上游仓库](https://github.com/lessweb/deepcode-cli)：项目身份、安装、命令、配置、Skills 和 MCP 说明。
- [上游配置文档](https://github.com/lessweb/deepcode-cli/blob/main/docs/configuration.md)：用户/项目设置、环境变量、权限和遥测配置。
- [上游 Releases](https://github.com/lessweb/deepcode-cli/releases)：版本发布记录。
- [npm 包](https://www.npmjs.com/package/@vegamo/deepcode-cli)：安装包与发布版本。
- [DeepSeek API 文档](https://api-docs.deepseek.com/)：模型 API、上下文缓存和思考模式。
- [DeepSeek API Keys](https://platform.deepseek.com/api_keys)：客户登录后创建和管理 API key。

身份边界：本技能中的 Deep Code 是 `lessweb/deepcode-cli` 开源项目，是专为 DeepSeek 模型优化的社区 Agent CLI；它不是 DeepSeek 官方组织发布的 CLI，也不是 HKUDS/DeepCode、Snyk DeepCode 或其他同名工具。若客户给出不同仓库，先停下并重新确认，不安装近似名称包。

已核对事实：npm 包名是 `@vegamo/deepcode-cli`；命令是 `deepcode`；包要求 Node.js 22 或更高版本；用户配置是 `~/.deepcode/settings.json`，项目配置是 `<project>/.deepcode/settings.json`；CLI 会发现 `~/.agents/skills` 和项目 `.agents/skills`；上游配置允许在文件中写 API key，但本技能不把秘密写入或回显到普通配置、日志和回执，优先使用客户现有的受保护凭据注入方式。真实启动时若缺少配置，CLI 会提示 `API key not found`；运行命令可初始化部分运行状态，但不会替客户生成包含秘密的 `settings.json`。
