---
name: soia-env-codex-setup-support
description: 诊断并支持 Codex 桌面版与 CLI 的安装、登录、性能和存储问题。触发：「Codex 打不开」「Codex 变慢」「检查 logs_2.sqlite」
dependencies:
  optional: [soia-env-network-diagnose, soia-env-node-install, soia-env-codex-install]
version: 1.4.3
created_at: 2026-07-20 18:30:00
updated_at: 2026-08-09 01:40:00
created_by: gpt-5
updated_by: deepseek-v4-flash
---

# soia-env-codex-setup-support

用本技能做 Codex 环境检查和安装支持。默认只读、分层推进、按需加载引用文件；除非客户明确确认，不安装、删除、移动、清理或修改系统和应用数据。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 交付形式 |
|---|---|---|
| 安装或验证 Codex | 检查版本、来源、桌面宿主和 CLI | 结果表 + 下一步 |
| 检查 Codex 更新 | 分别识别桌面应用与 CLI 的版本、来源和更新入口，不自动更新 | 当前版本、最新版本和建议 |
| 更新 Codex 到最新 | 客户明确要求最新版后分别更新桌面应用或 CLI | 中间状态、登录/签名复核和失败回滚边界 |
| Codex 变慢或卡住 | 按资源、日志、网络和工作区分类 | 分类表 + 证据 |
| 检查 SSD 健康 | 只读读取 SMART 和空间信息 | 健康度表 + 风险说明 |
| 检查 `logs_2.sqlite` | 只读比较文件、WAL、ID 速率和热点 | 写入风险表 + 处置边界 |

### 客户如何使用

直接描述目标，例如“检查磁盘健康”“Codex 变慢”“检查 logs_2.sqlite”。Agent 默认只读，发现新版本只汇报；只说“更新 Codex”时先询问是否更新到最新。登录、系统授权、安装和数据隔离会单独说明并请求确认。

### 依赖与安装

| 依赖 | 用途 | 规则 |
|---|---|---|
| macOS/Windows/Linux | 系统和架构识别 | 先识别，再选择平台分支 |
| `smartmontools` | macOS SMART 读取 | 不自动安装；需客户确认 |
| SQLite CLI | 日志数据库只读查询 | 缺失时报告未检查，不创建数据库 |
| Node/npm、网络技能 | CLI 安装和登录 | 只在进入对应分支时加载 |

装整个域（Claude Code 与 Codex 共用同一份域插件）：

```bash
claude plugin marketplace add soia-team/soia-open-skills
claude plugin install soia-env@soia
```

只装这一个技能：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-codex-setup-support -y
```

**WorkBuddy** 的装载单位是角色化专家而不是插件，`npx skills add -a '*'` 覆盖不到它，需要单独安装，见 [docs/install/workbuddy.md](https://github.com/soia-team/soia-open-skills/blob/main/docs/install/workbuddy.md)。

### 私密信息与中间数据

- Codex/ChatGPT 登录凭据由官方客户端、CLI 登录流程和系统凭据库管理；SOIA 配置只保存非秘密偏好与路径。
- 诊断默认只输出脱敏摘要，不复制数据库、日志正文、对话内容或 token；客户明确要求保存诊断回执时才写用户 state 目录，安装类变更必须使用进度记录器。回执只保留类别、数值、版本、结果和 `checked_at`，不记录账号、查询内容或客户私有绝对路径。

### 日志与完成回执

安装或明确授权的最新版更新必须边执行边显示以下阶段表，并在每个阶段实际发生时同步调用进度记录器；不得在结束后补写历史。只读诊断不创建安装记录：

| 阶段 | 当前状态 | 更新时间 | 处理结果 |
|---|---|---|---|
| <检查/计划/等待确认/安装或更新/验证/完成或失败> | <进行中/等待/已完成/失败/被阻塞> | <RFC3339-with-timezone> | <脱敏结果> |

使用结果表后，按以下最小格式收尾：

```markdown
结论：<类别>，<正常/预警/异常/未完成>。

解决方案：<已执行的只读检查；需确认的动作；没有执行的状态变更写 none>。

残余风险：<未检查项、不能归因的部分、复查条件>。
```

## 桌面版与 CLI 的边界

Codex 桌面能力由 OpenAI 官方 ChatGPT 桌面应用承载，不能再用是否存在独立 `Codex.app` 作为判断依据；macOS 优先核对 `ChatGPT.app` 的 bundle id `com.openai.codex`、版本和代码签名。桌面版与 CLI 的登录、版本、更新和工作区权限必须分别验证；`soia-env-codex-install` 保留为 CLI 专门安装技能。官方来源与桌面识别事实见 [official-sources.md](references/official-sources.md)。

## 交付规则

每次检查先给一张结果表，再给结论和下一步；不要把命令回显当成报告，也不要把未检查写成正常：

| 类别 | 检查项 | 结果 | 证据 | 风险 | 更新时间 | 下一步 |
|---|---|---|---|---|---|---|
| <A-F> | <具体指标> | <正常/预警/异常/未检查> | <简短数值或状态> | <低/中/高> | <RFC3339-with-timezone> | <动作或 none> |

`更新时间` 是该检查项最后取得证据的时间，不同检查项可以不同，不能用技能文件修改时间代替。表格后只保留三段：**结论**、**解决方案**（标明“只读”“需确认”或“未执行”）、**残余风险**。需要详细解释时先读对应 `references/` 文件；模板见 [operations.md](references/operations.md)。

## 渐进式流程

### 第 0 层：识别请求

从用户目标选择一个或多个类别（A 版本与安装 / B 网络与登录 / C 权限与工作区 / D 资源与渲染 / E SQLite 日志写放大 / F SSD 健康），不同时展开所有分支。“变慢”默认先查 D；只有出现磁盘、TRACE、WAL 或写入症状才进入 E。“SSD 写入量高”必须同时查 E 和 F，不能用日志库字节数直接代替 SSD 主机写入量。路由表见 [operations.md](references/operations.md)。

### 第 1 层：共同基线

只读采集 OS、架构、可用空间、桌面应用版本、CLI 版本、目标类别。桌面版和 CLI 可能共享 Codex home，CLI 能运行不代表桌面版或日志库正常；macOS 桌面识别用 `scripts/check_codex_desktop.py`，输出只作版本/签名证据。

### 第 2 层：单一问题分支

只加载当前分支需要的引用：A 读 [official-sources.md](references/official-sources.md)；B/C/D 先只读诊断，无证据不改代理、DNS、PATH、权限或工作区；E 读 [sqlite-log-diagnostics.md](references/sqlite-log-diagnostics.md) 做两次只读采样；F 读 [macos-disk-health.md](references/macos-disk-health.md)。

### 第 3 层：高级处置

只有第 2 层证据达到高风险，才讨论退出应用、备份、隔离或重建日志库；状态变更前展示目标、影响、备份位置和回滚方式并获客户确认。诊断请求到此结束，不顺手执行修复。

## 已安装状态与更新

桌面版和 CLI 必须分别判断；已安装且可用时提示“已安装，无需重复安装”。CLI 先执行 `codex --version`、`codex update --help`、`codex login status` 并记录来源，只有客户明确要求更新到最新后才更新。模糊的“更新 Codex”只做独立版本报告，写“等待确认是否更新到最新”；CLI 更新委托 `soia-env-codex-install`。完整细则见 [operations.md](references/operations.md)。

## 解决方案优先级

按优先级处置：1 建议更新桌面版/CLI，完全退出后重启复测（明确要求最新版后执行）；2 关闭重复进程、重新采样（需确认）；3 备份后隔离日志数据库（需确认）；4 `VACUUM`/触发器/改 WAL/RAM 盘（高风险，不默认提供执行命令）；5 SMART/硬件处置（需确认）。`VACUUM` 会重写数据库，不能阻止持续写入。适用条件见 [operations.md](references/operations.md)。

## 脚本与引用的使用边界

`scripts/check_codex_desktop.py` 只读识别 macOS ChatGPT 宿主、bundle id、版本和代码签名；`scripts/check_macos_disk.py` 只解析已取得的 SMART 摘要，不执行 `sudo`、长测或磁盘操作；`scripts/record_install_progress.py` 仅在本技能直接安装 `smartmontools`、桌面应用等安装类变更时记录。完整见 [operations.md](references/operations.md)。

## 前向测试

用四类样例验证结果表（SMART 正常/预警、SQLite 文件稳定/`MAX(id)` 推进但保留行数稳定），不得修改真实数据库或磁盘。

## 不负责什么（能力边界）

- **默认只读，不动系统**：不自动 `sudo`、安装包、改 PATH/profile、代理/DNS、权限、数据库或工作区；不执行删除、覆盖、格式化、分区、固件升级、`VACUUM`、数据库 checkpoint、触发器或日志清理，除非客户看到明确计划后单独确认。
- **不代客户认证**：客户只在官方 UI 完成登录、验证码和系统授权，不要求客户在终端输入秘密。
- **不重复发明 CLI 安装**：CLI 安装/更新委托 `soia-env-codex-install`；桌面应用只能用应用内或官方更新入口更新。
- **不做无证据归因**：npm 返回 0 不等于登录完成，SMART `PASSED` 不等于整机绝对正常。
