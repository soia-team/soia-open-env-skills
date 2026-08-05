---
name: soia-env-workbuddy-install
description: 为新手安装、验证或按授权更新 WorkBuddy 桌面客户端。触发：「安装 WorkBuddy」「更新 WorkBuddy」「WorkBuddy 下载」
dependencies:
  optional: [soia-env-network-diagnose]
version: 1.5.2
created_at: 2026-07-20 18:00:00
updated_at: 2026-08-05 13:30:00
created_by: gpt-5
updated_by: claude-opus-5
---

# soia-env-workbuddy-install

WorkBuddy 是桌面应用，安装路径与 Node/Python 不同。先打开官方站点和下载页，选择对应系统安装包，再由客户完成系统安全提示、登录和服务授权。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 安装 WorkBuddy | 识别系统/架构并打开官方下载安装入口 | 官方下载链接和安装状态 |
| 检查 WorkBuddy 更新 | 识别已安装版本、来源和签名，不自动更新 | 当前版本、最新版本和签名 |
| 更新 WorkBuddy 到最新 | 客户明确要求最新版后沿用官方更新路径 | 中间状态、签名和启动验证 |
| WorkBuddy 打不开 | 检查安装结果、签名提示、网络和版本 | 可复现的阻塞类别与下一步 |
| 不会登录 | 引导官方界面登录 | 客户自己完成授权，不交出密码 |

### 客户如何使用

其他可识别说法包括「更新 WorkBuddy 到最新」「安装腾讯龙虾」「WorkBuddy 打不开」。

1. 说“安装 WorkBuddy”并说明系统；Agent 先确认系统和芯片架构。
2. Agent 只使用官方 `workbuddy.cn` 下载入口，不下载来路不明的 DMG/EXE。
3. 已安装时发现新版本只汇报；只说“更新 WorkBuddy”时先询问是否更新到最新，明确选择最新版后才执行。
4. 客户在系统安装器中完成打开、拖拽、权限和登录；Agent 不要求客户使用终端。
5. 安装或明确授权的更新过程中持续显示并记录检查、计划、执行、验证和终态。

### 首次启动与真实可用性验证

- 应用文件存在只代表“已安装”，不代表登录、服务授权和工作区已经可用。
- 安装完成后由 Agent 启动 WorkBuddy，客户在官方图形界面完成登录、验证码、系统安全提示和服务授权；Agent 不代填密码。
- Agent 重新检查应用启动、账号状态和一次无副作用工作区操作；其中任一步未完成，运行状态写“未验证”，处理结果写“等待首次登录/授权”，不伪报“正常”。

### 装完之后

本技能只负责**客户端本身**。把 SOIA 技能装进 WorkBuddy 是另一件事，
由 `soia-meta-skill-release` 负责——客户说「装到 WorkBuddy」即可触发。

### 依赖与安装

无 Node/Python 依赖。官方入口、当前可见平台和安装后验证边界见 [official-sources.md](references/official-sources.md)。网络异常时调用 `soia-env-network-diagnose`。

## 标准流程

1. 只读识别 `macOS/Windows`、CPU 架构、已安装应用版本、签名和当前用户是否能安装应用；Linux 先说明官方桌面支持范围未验证。
2. 打开官方站点的产品下载入口：macOS 区分 ARM64/x64，Windows 选择 x64/兼容 ARM64 版本；不猜测下载 URL。
3. 展示安装动作和系统权限影响，客户确认后再启动安装器。
4. 客户在官方 UI 完成安全提示、登录、验证码和隐私/服务授权；Agent 不代填。
5. 验证应用启动、版本或“关于”页面；若只能确认安装包落地，明确标注剩余验证。

## 已安装状态与更新

先检查已经存在的应用；状态正常时提示“WorkBuddy 已安装，无需重复安装”，不覆盖、不卸载，也不把再次下载当作默认更新方式。

- macOS 记录应用版本、安装位置，并执行 `codesign --verify --deep --strict <WorkBuddy.app>`；可用时再执行 `spctl --assess --type execute <WorkBuddy.app>`。
- Windows 记录“应用和功能”中的版本、发布者和系统安全提示；不关闭 SmartScreen 或杀毒软件。
- 已安装且签名/发布者验证通过：先展示目标版本和影响；只有客户明确要求更新到最新后，才从 WorkBuddy 官方站点或应用内官方更新入口执行。
- 应用存在但签名验证失败、发布者不明或版本无法读取：标记为 `invalid_signature` 或 `installed_unverified`，先处理来源问题，不提示“安装正常”。
- WorkBuddy 没有本技能承诺的 npm/CLI 更新路径；不使用 `npm`、未知下载脚本或第三方镜像更新。

更新前保留旧版本、来源和验证结果。更新失败时保留旧版本和错误证据，不自动卸载、删除用户数据或绕过系统安全策略。

模糊的“更新 WorkBuddy”只执行版本比较并返回“等待确认是否更新到最新”。明确安装缺失的 WorkBuddy 可以安装官方当前推荐版本，不视为更新现有应用。

## 客户状态列表（强制）

| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|
| WorkBuddy | <已安装/未安装/被阻塞> | <版本或未取得> | <版本或未取得> | <正常/异常/未验证> | <RFC3339-with-timezone> | <无需重复安装/可更新，未执行/等待确认是否更新到最新/已更新/等待确认后安装/被阻塞：原因> |

- 只输出 WorkBuddy 行，不增加 Node.js、Python、npm 或其他工具行。
- `更新时间` 记录版本、签名和启动验证完成后的时间。
- 签名或发布者验证失败时，`运行状态` 写“异常”，`处理结果` 写明来源阻塞。
- 表格后只保留必须由客户在官方 UI 完成的安装、登录或系统安全步骤。

## 安装与更新的中间状态

真正执行安装或获得最新版授权的更新时，用随机 `run_id` 在阶段实际发生时立即调用 `scripts/record_install_progress.py`：检查前、方案形成后、安装器/更新器调用前、签名与启动验证前和终态各记录一次；需要管理员权限或切换来源时再记录 `waiting_confirmation`。不得结束后补写；时间由记录器生成。只读检查不调用。只有客户原话明确要求最新版时，更新执行阶段才带 `--customer-requested-latest`。

```bash
python3 scripts/record_install_progress.py --run-id <run-id> --action <install|update> --stage checking --status in_progress --result-code checking_started
python3 scripts/record_install_progress.py --run-id <run-id> --action update --stage updating --status in_progress --result-code update_started --customer-requested-latest
```

同时持续展示固定阶段表；成功、失败、取消或等待系统操作时都要追加终态：

| 阶段 | 当前状态 | 更新时间 | 处理结果 |
|---|---|---|---|
| <检查/计划/等待确认/安装或更新/验证/完成或失败> | <进行中/等待/已完成/失败/被阻塞> | <RFC3339-with-timezone> | <脱敏结果> |

## 权限与回滚

- 不关闭 Gatekeeper、SmartScreen、杀毒软件或系统安全策略。
- 不删除旧版本；新旧版本冲突时先停止并让客户选择。
- 卸载、清理用户数据或撤销授权必须作为单独请求，不能作为安装失败的自动回滚。

## 私密信息与中间数据

- WorkBuddy 账号、token 和会话只保留在官方客户端登录态或系统凭据库；SOIA 配置只保存非秘密偏好。
- 安装或更新阶段使用进度记录器追加脱敏的动作、阶段、结果和时间；只读检查默认不落盘。
- 下载元数据可放 cache，安装器和签名检查中间文件放系统临时目录并在成功或失败后清理。
- 不复制客户端用户数据，不记录账号、会话、聊天内容或客户私有绝对路径。

## 日志与完成回执

```markdown
| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 更新时间 | 处理结果 |
|---|---|---|---|---|---|---|
| WorkBuddy | <状态> | <当前版本> | <最新版本> | <运行状态> | <RFC3339-with-timezone> | <处理结果> |
```

## 前向测试

用平台 fixture 验证 macOS ARM64、macOS x64、Windows x64 和未知平台的选择逻辑；真实验收必须由客户确认官方安装器和登录页面，不把网页可达当成客户端可用。

装整个域（Claude Code 与 Codex 共用同一份域插件）：

```bash
claude plugin marketplace add soia-team/soia-open-skills
claude plugin install soia-env@soia
```

只装这一个技能：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-workbuddy-install -y
```
