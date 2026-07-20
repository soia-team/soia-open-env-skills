# Node.js 官方来源（2026-07-20 核对）

- 官网：[Node.js](https://nodejs.org/en)
- 下载与版本说明：[Node.js Releases](https://nodejs.org/en/about/previous-releases)
- 官方页面当前区分 Latest LTS 与 Latest Release；默认选择 LTS，除非项目明确要求其他版本。

## 选择规则

- 先读项目的 `.nvmrc`、`package.json`、CI 配置或文档，再决定版本。
- 初学者优先使用官方安装器，或在团队已有约定时使用一个版本管理器；不要同时引入多个版本管理器。
- 安装后分别验证 `node --version` 与 `npm --version`，并检查 `npm config get prefix`。
- 不使用未经客户确认的镜像源、全局业务依赖或管理员权限。
