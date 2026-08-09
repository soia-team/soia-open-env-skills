# 操作细则（桌面边界 / 更新 / 脚本边界 / 安全边界）

## 桌面版与 CLI 的边界

- Codex 桌面能力由 OpenAI 官方 ChatGPT 桌面应用承载；不能再用是否存在独立 `Codex.app` 作为判断依据。macOS 优先核对 `ChatGPT.app` 的 bundle id `com.openai.codex`、版本和代码签名。
- CLI 使用官方 `@openai/codex` 或官方独立安装入口；桌面版和 CLI 的登录、版本、更新和工作区权限必须分别验证。
- `soia-env-codex-install` 保留为 CLI 专门安装技能；本技能负责桌面版、CLI 与故障排查的编排，不重复发明登录流程。

## 已安装状态与更新细则

- CLI 先执行 `codex --version`、`codex update --help`、`codex login status`，并记录 `command -v codex` 与安装来源。
- CLI 支持 `codex update` 时，也只有客户明确要求更新到最新后才使用；npm 管理且不支持内置更新时才使用 `npm install -g @openai/codex@latest`；独立安装器管理时沿用官方 CLI 文档的更新入口。
- ChatGPT 桌面应用（Codex 宿主）只有在客户明确要求桌面版更新到最新后，才通过应用内或官方桌面应用更新入口更新；不能用 CLI 的 `codex update` 代替桌面应用更新。
- macOS 更新后重新执行桌面识别脚本，确认 `com.openai.codex`、版本和代码签名；CLI 更新后重新验证版本、帮助和登录状态。更新版本不等于重新登录，不强制客户重复授权。
- 更新前记录旧版本、来源和关键验证结果；更新失败时保留现有安装，不自动卸载、清理日志或删除应用数据。

## 脚本与引用的使用边界

- `scripts/check_codex_desktop.py`：只读识别 macOS ChatGPT 宿主、bundle id、版本和代码签名。
- `scripts/check_macos_disk.py`：只解析已经取得的 SMART 摘要，不执行 `sudo`、长测或任何磁盘操作。
- `scripts/record_install_progress.py`：仅在本技能直接安装 `smartmontools`、桌面应用或执行其他安装类变更时追加私有阶段记录；CLI 更新由 `soia-env-codex-install` 记录。
- `references/`：存放命令、字段解释、平台差异、阈值和高级处置；只在进入对应分支时加载。
- 不在 `SKILL.md` 中新增大段 shell、SQL、PowerShell 或原始供应商说明；重复使用的确定性逻辑优先进入脚本，解释性内容进入引用文件。

## 解决方案优先级

| 优先级 | 动作 | 默认权限 | 适用条件 |
|---|---|---|---|
| 1 | 建议更新桌面版/CLI，完全退出后重启并复测 | 明确要求最新版后执行 | 版本旧或 E 分支出现写放大 |
| 2 | 关闭重复进程、减少复现范围、重新采样 | 需客户确认 | 没有活动任务且确认进程持有关系 |
| 3 | 备份后隔离日志数据库，让应用重建 | 需客户确认 | E 分支达到高风险，且无进程持有 |
| 4 | `VACUUM`、触发器、改 WAL、RAM 盘 | 高风险，不默认提供执行命令 | 仅高级维护人员明确选择；这些不是首选修复 |
| 5 | SMART/硬件处置 | 需客户确认 | F 分支出现错误、寿命或温度预警；先备份 |

`VACUUM` 会重写数据库，不能阻止持续写入；macOS 的 `/tmp` 通常仍在 SSD 上，也不能当成 RAM 盘。切换到 CLI 也不是 E 分支的可靠修复。

## 安全边界细则

- 默认只读；不自动 `sudo`、安装包、修改 PATH/profile、代理/DNS、权限、数据库或工作区。
- 客户只在官方 UI 完成登录、验证码和系统授权；不要求客户在终端输入秘密。
- 不执行删除、覆盖、格式化、分区、固件升级、`VACUUM`、数据库 checkpoint、触发器或日志清理，除非客户在看到明确计划后单独确认。
- 真实验收不能把 npm 返回 0 当成登录完成，也不能把 SMART `PASSED` 当成整机绝对正常。

## 第 0 层：识别请求路由表

| 类别 | 触发症状 | 第一层证据 | 详细流程 |
|---|---|---|---|
| A 版本与安装 | 未安装、打不开、旧版本 | OS、架构、桌面/CLI 版本、官方来源 | 官方来源与桌面识别脚本 |
| B 网络与登录 | 下载失败、登录循环、API 不通 | DNS/HTTPS、浏览器授权、组织权限 | `soia-env-network-diagnose` |
| C 权限与工作区 | 目录不能读写、任务不能启动 | 目录权限、Git、项目依赖 | 最后检查工作区，不误判安装故障 |
| D 资源与渲染 | CPU/RSS 高、长线程卡顿、界面无响应 | 进程资源、复现时间、线程规模 | 应用/资源分支，必要时与 E 并查 |
| E SQLite 日志写放大 | `logs_2.sqlite`/WAL 变大、TRACE 高频、SSD 写入异常 | 文件快照、`MAX(id)` 速率、热点 target、持有进程 | [sqlite-log-diagnostics.md](sqlite-log-diagnostics.md) |
| F SSD 健康 | SMART 预警、寿命高、温度或错误异常 | 物理设备、SMART、空间 | [macos-disk-health.md](macos-disk-health.md) |

## 第 1 层：共同基线

- 只读采集最小信息：操作系统和架构、可用空间、桌面应用版本、CLI 版本、目标类别；不打印完整用户名、token、cookie、API key、密码或完整本地路径。
- 桌面版和 CLI 可能共享 Codex home；不能因为 CLI 能运行就推断桌面版或日志数据库正常。
- macOS 桌面识别使用 `scripts/check_codex_desktop.py`，输出只作为版本/签名证据。

## 第 2 层：单一问题分支

- A：读取 [official-sources.md](official-sources.md)，缺 Node/npm 或 CLI 时再调用对应依赖技能。
- B/C/D：先执行只读诊断；没有证据时不修改代理、DNS、PATH、权限或工作区。
- E：完整读取 [sqlite-log-diagnostics.md](sqlite-log-diagnostics.md)，使用只读 SQLite 连接并做两次采样。
- F：完整读取 [macos-disk-health.md](macos-disk-health.md)，先确认物理设备，再读取 SMART；不自动安装 `smartmontools`。

## 第 3 层：高级处置

只有第 2 层证据达到高风险，才讨论退出应用、备份、隔离或重建日志库；状态变更前必须展示目标、影响、备份位置和回滚方式，并获得客户确认。诊断请求到此结束，不顺手执行修复。

## 交付结果表模板

| 类别 | 检查项 | 结果 | 证据 | 风险 | 更新时间 | 下一步 |
|---|---|---|---|---|---|---|
| <A-F> | <具体指标> | <正常/预警/异常/未检查> | <简短数值或状态> | <低/中/高> | <RFC3339-with-timezone> | <动作或 none> |

## 前向测试

至少用四类样例验证结果表：SMART 正常、SMART 预警、SQLite 文件稳定、SQLite `MAX(id)` 推进但保留行数稳定。验证不得修改真实数据库或磁盘。

## 安装/更新阶段表模板

| 阶段 | 当前状态 | 更新时间 | 处理结果 |
|---|---|---|---|
| <检查/计划/等待确认/安装或更新/验证/完成或失败> | <进行中/等待/已完成/失败/被阻塞> | <RFC3339-with-timezone> | <脱敏结果> |
