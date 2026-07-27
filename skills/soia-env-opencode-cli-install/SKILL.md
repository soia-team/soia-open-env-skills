---
name: soia-env-opencode-cli-install
description: 为小白安装、登录、配置与授权更新开源 OpenCode CLI。触发：「安装 OpenCode」「opencode 命令不存在」
dependencies:
  optional: [soia-env-node-install, soia-env-network-diagnose]
version: 1.0.2
created_at: 2026-07-21 00:00:00
updated_at: 2026-07-27 10:51:45
created_by: gpt-5
updated_by: claude opus 5
---

# soia-env-opencode-cli-install

安装和验证 OpenCode CLI（命令 `opencode`）。Agent 负责终端操作；客户只在所选模型供应商的官方页面完成登录或授权。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装 OpenCode | 检查已有来源并用官方稳定渠道安装 | 版本、来源、安装和配置目录 |
| 检查或更新 | 比较 GitHub 官方最新 release；明确授权后沿原来源升级 | 可更新状态或“已更新” |
| 配置模型供应商 | 只处理非秘密设置并启动官方认证 | 配置位置和浏览器下一步 |
| 命令不可用 | 检查 PATH、重复副本和配置覆盖 | 阻塞原因与修复方案 |

### 客户如何使用

1. 客户说“安装 OpenCode”；不要求客户复制终端命令。
2. Agent 先只读检查并展示计划；安装缺失 CLI 不授权更新已有 CLI。
3. 模糊“更新 OpenCode”只显示当前版和最新版；明确“更新到最新”才执行升级。
4. 配置或登录时不索要 API key；有官方 OAuth/浏览器流程就由客户在官方页面完成。
5. 完成后验证版本、帮助命令和无副作用启动，再输出一行固定状态。

### 首次配置与真实认证验证

- `~/.config/opencode` 是配置候选目录；供应商凭据通常由 `opencode auth login` 写入 `~/.local/share/opencode/auth.json`，两者必须分开检查，不能把一个不存在的目录当成已配置。
- 首次配置由 Agent 启动 `opencode auth login`，客户在供应商官方页面完成 OAuth 或在官方交互界面输入凭据；Agent 不接收、不回显 API key。
- 完成后运行 `opencode auth list`，再启动 OpenCode 并执行无副作用的模型/帮助检查；没有供应商凭据时处理结果写“等待供应商登录/配置”。
- 只有需要自定义模型或项目设置时才创建 `~/.config/opencode/opencode.json` 或项目 `opencode.json`；默认配置文件不存在不等于 CLI 安装失败。

### 依赖与安装

| 依赖 | 类型 | 缺失时怎么处理 |
|---|---|---|
| 官方支持的操作系统 | 强依赖 | 不支持时停止并说明 |
| Node.js/npm | npm 渠道依赖 | 独立安装和 Homebrew 不需要；npm 渠道才调用 `soia-env-node-install` |
| 网络诊断 | 可选前置 | 官方站点或供应商登录失败时调用 `soia-env-network-diagnose` |
| 模型供应商账号 | 运行依赖 | 客户选择供应商并在官方界面授权；不读取秘密 |

官方来源见 [official-sources.md](references/official-sources.md)。

## 标准流程

1. 执行 `python3 scripts/inspect_cli.py --json`，只读检测 `opencode`、版本、来源、安装目录、配置覆盖路径及配置文件的实际存在状态。
2. 执行 `python3 scripts/check_latest.py --json`，从 `anomalyco/opencode` 官方 GitHub latest release 获取最新版。
3. 已安装且正常时写“已安装”；没有明确最新版授权就停止，不执行启动时更新或安装器。
4. 未安装时优先官方独立渠道；客户选择 npm 时使用 `npm install -g opencode-ai`，选择 Homebrew 时使用官方 tap。网络脚本先下载到独立临时目录并检查，再执行本地副本；不直接执行网络响应。
5. 明确更新到最新后，优先用当前绝对路径执行 `opencode upgrade` 并保持来源；npm/Homebrew 来源也可沿检测到的包管理器更新。不得静默换源。
6. 验证同一命令的 `--version`、`--help` 和无副作用启动。需要模型登录时启动 OpenCode 官方认证流程，把浏览器交给客户。
7. 重新检测版本、目录和配置，使用 `scripts/render_status.py` 输出客户列表。

## 产品自动更新边界

- OpenCode 可能在启动时检查并下载更新；本技能默认不调用更新器，但要披露产品的 `autoupdate` 行为。
- 只读检查不得把 `autoupdate` 改为 `false`、`notify` 或其他值。
- 客户要求改变自动更新设置时，先展示影响并单独确认；配置变更不等于授权本次升级。

## 客户状态列表（强制）

回复必须以以下十列表格开头，只输出一行 `OpenCode CLI`：

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 安装方式 | 安装目录 | 配置文件目录 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|---|---|---|
| OpenCode CLI | <已安装/未安装/被阻塞> | <版本或未取得> | <版本或未取得> | <正常/异常/未验证> | <官方独立安装/Homebrew 安装/npm 全局安装/未取得> | <目录或未取得> | <目录或未取得> | <RFC3339-with-timezone> | <已安装/已是最新/可更新，未执行/等待确认是否更新到最新/已更新/等待登录/被阻塞：原因> |

- 用户只问 OpenCode CLI 时，不增加 Node.js、npm、模型供应商或其他技能行。
- `更新时间` 是最终验证时间；目录用 `~` 相对路径，避免用户名。
- 已更新仍写“已安装”；多个副本只汇报登录 shell 生效的一份并提示冲突，不自动删除。
- 最新版取得失败写“未取得”，不猜测。
- `config_status=未创建` 且凭据状态未发现时，处理结果写“等待供应商登录/配置”；如果只有凭据文件而没有 `opencode.json`，必须说明这是正常的认证存储位置，不要求客户重复创建配置文件。

## 安装与更新的中间状态

真正安装或更新时生成随机 `run_id`，每个实际阶段立即调用 `scripts/record_install_progress.py`，同步展示检查、计划、等待确认、安装/更新、验证和终态。只读检查不创建 state。

| 阶段 | 当前状态 | 更新时间 | 处理结果 |
|---|---|---|---|
| <检查/计划/等待确认/安装或更新/验证/完成或失败> | <进行中/等待/已完成/失败/被阻塞> | <RFC3339-with-timezone> | <脱敏结果> |

更新的执行和验证阶段必须带客户明确最新版授权标记。事件只保存固定结果代码和时间，不保存命令全文、供应商响应、token、账号或私有路径。

## 权限与回滚

- 优先用户级安装，不默认使用 `sudo`。修改 PATH、覆盖配置、切换安装来源或系统范围安装先确认。
- 更新前记录旧版本和来源；失败时保留原安装，不自动卸载、降级或重置配置。
- 安装脚本只存在于系统临时目录，成功、失败或取消都清理。

## 私密信息与中间数据

- 凭据由供应商官方 OAuth/登录态、OpenCode 的官方凭据存储或系统凭据库管理；不读取或回显。
- 非秘密配置留在 `~/.config/opencode` 或客户明确的覆盖路径；SOIA 不复制秘密。
- 机器变更阶段记录写用户私有 state；版本检查默认无状态。
- 不记录 API key、token、cookie、授权码、账号、响应正文或客户私有绝对路径。

## 日志与完成回执

最终回执包含固定十列表格、验证项、自动更新设置是否只读，以及客户是否还需浏览器登录。正常依赖不展开成额外行。

## 前向测试

用临时 fake `opencode` 覆盖缺失、正常、异常和多副本；mock GitHub release；验证十列渲染、配置覆盖、路径脱敏、默认不更新和更新授权门禁。
