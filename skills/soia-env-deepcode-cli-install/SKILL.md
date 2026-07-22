---
name: soia-env-deepcode-cli-install
description: 为小白安装、配置与授权更新开源 Deep Code Agent CLI（lessweb/deepcode-cli）。触发：「安装 DeepCode」「deepcode 不存在」「配置 DeepSeek Agent」。
dependencies:
  hard: [soia-env-node-install]
  optional: [soia-env-network-diagnose]
version: 1.0.2
created_at: 2026-07-21 00:00:00
updated_at: 2026-07-23 07:16:11
created_by: gpt-5
updated_by: gpt-5
---

# soia-env-deepcode-cli-install

安装和验证 `lessweb/deepcode-cli`（命令 `deepcode`，npm 包 `@vegamo/deepcode-cli`）。它是面向 DeepSeek 模型优化的社区开源 Agent CLI，不是 HKUDS、Snyk 或其他同名 DeepCode 产品。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装 Deep Code | 核对项目身份、Node.js 22 和 npm，再安装上游包 | 版本、来源、安装和配置目录 |
| 检查或更新 | 从 npm 官方元数据比较版本；明确授权后沿 npm 更新 | 可更新状态或“已更新” |
| 配置 DeepSeek | 检查非秘密模型和地址设置，保护 API key | 配置位置与本地安全配置下一步 |
| 命令不可用 | 检查 PATH、npm 全局目录和同名命令 | 阻塞原因与修复方案 |

### 客户如何使用

1. 客户说“安装 Deep Code CLI”；Agent 先确认目标是 `lessweb/deepcode-cli`，客户不需要操作终端。
2. Agent 只读检查 `deepcode`、Node.js、npm、实际包来源和版本，再展示计划。
3. 安装请求只授权安装缺失 CLI；已有版本默认不更新。模糊“更新”只显示版本，明确“更新到最新”才执行。
4. 运行需要模型凭据时，客户在 DeepSeek 官方平台自行创建或管理 key；不得把 key 发到聊天中。Agent 只指导本机受保护输入或使用客户已有的安全凭据注入。
5. 完成后验证版本、帮助命令和一次无副作用启动；未配置凭据时如实写“已安装，等待本地配置”，不伪报运行正常。

### 首次配置与真实验证

- `~/.deepcode` 只是默认数据目录；必须同时检查目录和 `~/.deepcode/settings.json`。目录存在不代表 API key 已配置。
- 首次启动 `deepcode` 会初始化部分本地运行状态，但不会替客户生成包含 API key 的 `settings.json`；真实验收已经验证，没有 key 时 CLI 会明确提示 `API key not found`。
- 客户在 [DeepSeek API Keys](https://platform.deepseek.com/api_keys) 登录并创建 API key。客户只在本机填写，不把 key 发给 Agent。
- 客户在本机创建 `~/.deepcode/settings.json`，最小非秘密结构如下；`API_KEY` 只在客户本机替换：

  ```json
  {
    "env": {
      "MODEL": "deepseek-v4-pro",
      "BASE_URL": "https://api.deepseek.com",
      "API_KEY": "<仅在本机填写>"
    }
  }
  ```

- Agent 重新检查 `config_status`、`config_file_status`，再启动 `deepcode` 做一次无副作用验证；只有实际请求成功，运行状态才写“正常”。

### 依赖与安装

| 依赖 | 类型 | 缺失时怎么处理 |
|---|---|---|
| Node.js 22+ 与 npm | 强依赖 | 调用 `soia-env-node-install` 安装兼容稳定版本；不得用旧 Node 强装 |
| 网络诊断 | 可选前置 | npm、GitHub 或 DeepSeek API 不可达时调用 `soia-env-network-diagnose` |
| DeepSeek/兼容供应商凭据 | 运行依赖 | 客户本机安全配置，不发到聊天或日志 |
| HKUDS/DeepCode、Snyk DeepCode | 非依赖 | 同名但不是本技能目标，禁止混装 |

身份、包名和配置事实见 [official-sources.md](references/official-sources.md)。

## 标准流程

1. 执行 `python3 scripts/inspect_cli.py --json`，只读检测 `deepcode`、版本、路径、npm 来源、`~/.deepcode` 目录和 `settings.json` 的实际存在状态。
2. 读取实际 `node --version` 和 npm 全局包来源；Node.js 低于 22 时先报告阻塞，不运行安装包。
3. 执行 `python3 scripts/check_latest.py --json`，从 npm 官方元数据读取 `@vegamo/deepcode-cli` 最新版。
4. 若命令由其他包提供，写“被阻塞：同名命令来源不匹配”，不覆盖。已安装上游包且正常时写“已安装”，默认不更新。
5. 未安装时由 Agent 执行 `npm install -g @vegamo/deepcode-cli`；如 npm 全局目录需管理员权限，先提供用户级替代方案并确认，不默认 `sudo`。
6. 明确更新到最新时才执行 `npm install -g @vegamo/deepcode-cli@latest`。记录旧版和 npm prefix，不切换为 Git 仓库开发安装。
7. 验证同一绝对路径的 `--version`、`--help` 和 npm 包身份。客户请求安装/配置或真实测试且配置缺失时，Agent 启动一次 `deepcode` 初始化运行状态；如果 CLI 返回 `API key not found`，停止在配置引导，不伪报成功。凭据已安全配置时再做无副作用启动；否则运行状态写“未验证”。
8. 复查版本和目录，使用 `scripts/render_status.py` 输出一行客户状态。

## 凭据配置边界

- 上游允许在 `settings.json` 的 `env.API_KEY` 写值，但普通 JSON 文件不是首选凭据库；技能不得替客户把 key 写进公开配置、项目文件、日志或回执。
- 优先使用客户已有的本机安全注入或受保护的用户级凭据方案；如产品能力迫使使用凭据文件，先说明风险，限定为用户配置目录并设置仅当前用户可读。
- 客户不在聊天中提供密钥。Agent 不读取密钥内容，只验证“是否存在/是否可认证”的结果类别。
- 项目 `.deepcode/settings.json` 可能进入 Git；任何密钥写入项目配置一律拒绝。

## 客户状态列表（强制）

回复必须以以下十列表格开头，只输出一行 `Deep Code CLI`：

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 安装方式 | 安装目录 | 配置文件目录 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|---|---|---|
| Deep Code CLI | <已安装/未安装/被阻塞> | <版本或未取得> | <版本或未取得> | <正常/异常/未验证> | <npm 全局安装/未取得> | <目录或未取得> | <目录或未取得> | <RFC3339-with-timezone> | <已安装/已是最新/可更新，未执行/等待确认是否更新到最新/已更新/等待本地配置/被阻塞：原因> |

- 用户只问 Deep Code CLI 时，不增加 Node.js、npm、DeepSeek 模型或其他技能行；Node.js 仅在阻塞时压缩进 `处理结果`。
- `更新时间` 在最终验证后生成；目录用 `~` 相对路径，避免用户名。
- 已更新时 `当前状态` 仍写“已安装”。来源不匹配时不得仅凭命令名写“已安装”。
- 最新版取得失败写“未取得”，不猜测。
- `config_status=未创建` 或 `config_file_status=未创建` 时，处理结果必须写“等待首次配置”，并给出 DeepSeek API Keys 入口和本机配置文件位置；不得只报一个默认目录。

## 安装与更新的中间状态

真正安装或更新时生成随机 `run_id`，每个实际阶段立即调用 `scripts/record_install_progress.py`，同步展示检查、计划、等待确认、安装/更新、验证和终态。只读检查不创建 state。

| 阶段 | 当前状态 | 更新时间 | 处理结果 |
|---|---|---|---|
| <检查/计划/等待确认/安装或更新/验证/完成或失败> | <进行中/等待/已完成/失败/被阻塞> | <RFC3339-with-timezone> | <脱敏结果> |

更新执行和验证阶段必须带客户明确最新版授权标记。记录只保存固定结果代码和时间，不保存 npm 输出正文、API key、账号、命令全文或私有路径。

## 权限与回滚

- 优先用户级 npm prefix，不默认使用 `sudo`。修改 PATH/profile、覆盖同名命令或系统范围安装先确认。
- 更新前记录旧版本和包身份；失败时保留旧安装，不自动卸载、降级或删除配置。
- 安装不得改写项目 `package.json` 或 lockfile。

## 私密信息与中间数据

- API key 留在客户认可的本机安全位置；SOIA 配置、审计 state 和回执不保存秘密。
- 非秘密设置可留在 `~/.deepcode/settings.json`；项目配置只保存可提交的非秘密设置。
- 机器变更阶段记录写用户私有 state；版本检查默认无状态。
- 不记录 token、key、账号、提示词、代码内容、响应正文或客户私有绝对路径。
- `deepcode` 没有替代 OAuth 的独立登录命令；首次配置的关键动作是客户申请 DeepSeek API key、在本机填写 `settings.json`，然后由 Agent 重新验证。

## 日志与完成回执

最终回执包含固定十列表格、包身份、Node.js 是否满足、验证项，以及客户是否还需在本机配置凭据。正常依赖不展开成额外行。

## 前向测试

用临时 fake `deepcode` 覆盖缺失、正常、错误包来源和版本异常；mock npm 最新版；验证 Node.js 22 门禁、十列列表、路径脱敏、默认不更新和明确授权门禁。
