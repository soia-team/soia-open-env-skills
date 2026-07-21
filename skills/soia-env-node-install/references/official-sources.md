# Node.js 官方来源（2026-07-20 核对）

- 官网：[Node.js](https://nodejs.org/en)
- 下载与版本说明：[Node.js Releases](https://nodejs.org/en/about/previous-releases)
- 官方页面当前区分 Latest LTS 与 Latest Release；默认选择 Active LTS，除非项目明确要求其他版本。Current 版本不作为生产默认值。

## 选择规则

- 先读项目的 `.nvmrc`、`package.json`、CI 配置或文档，再决定版本。
- 初学者优先使用官方安装器，或在团队已有约定时使用一个版本管理器；不要同时引入多个版本管理器。
- 安装后分别验证 `node --version` 与 `npm --version`，并检查 `npm config get prefix`。
- 更新前先识别 Homebrew、nvm 或官方安装器来源；版本检查默认只读，只有客户明确要求“更新到最新版本”时才沿用现有来源执行，避免混装。
- Homebrew 更新：`brew update && brew upgrade node`；nvm 更新：`nvm install --lts`，具体版本以官方发布页和项目约束为准。
- 不使用未经客户确认的镜像源、全局业务依赖或管理员权限。
