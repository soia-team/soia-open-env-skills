# 执行流程与状态输出细则

## 完整执行流程

1. 识别 OS、版本、架构、shell、当前用户权限和项目目录。运行时盘点走 `soia-env-network-diagnose` 的 `scripts/probe_runtimes.py --json`，**不要自己临场拼版本命令**——各运行时的版本参数不一致（`go` 不认 `--version`、`java` 把版本写进 stderr、`rustc` 冷启动会超时），该脚本已按工具适配并有测试锁住。
2. 把目标拆成 `network → runtime → package manager → AI tool → downstream handoff`。
3. 用 `soia-env-network-diagnose` 的只读流程分两侧检查：网络侧按三组对照探测官方站点，本机侧按类别盘点运行时并给出各 AI CLI 的「可安装 / 待复核 / 被阻塞」。出现代理、证书、DNS 或超时问题时，先输出诊断，不自动改网络配置；运行时状态为 `timeout` 时判「待复核」并放宽超时复核，**不得当成未安装直接触发安装**。
4. 按依赖顺序执行：选择 npm 渠道的 Agent CLI 先满足对应 Node.js 要求；Deep Code 固定要求 Node.js 22+；Claude Code、Qoder、OpenCode、Kimi Code 有独立安装时不因 Node.js 缺失而阻塞；Antigravity 使用 Google 独立安装；Python 工作流先准备 Python/venv；WorkBuddy 使用官方桌面安装包。
5. 对已安装工具默认只比较版本；没有明确“更新到最新”时不得进入专门技能的更新执行阶段。
6. 安装或明确授权的更新由专门技能边执行边显示阶段状态并记录私有进度；每一步完成后验证命令、版本、路径和一次无副作用的 `--help`/版本调用。对需要登录或 API key 的 CLI，还必须完成首次配置和真实认证验证；否则标记为 `needs_configuration`。
7. 客户提出空间清理时调用 `soia-env-storage-cleanup`：本编排只能推进扫描和计划，必须等客户看过风险清单并明确授权后才能删除。

## 客户状态列表输出规则

- 只列客户要求的目标及其必要前置项，不把所有已安装工具全部展开。
- `更新时间` 是该行完成最终验证的时间，不是技能文件的修改时间。
- 网络诊断的版本列写“不适用”；无法取得软件最新版本时写“未取得”。
- 内部依赖检查正常时不单独成行；只有它阻塞目标时才增加前置项行。
- 机器可读 YAML/JSON 摘要在客户列表之后提供，并保持固定结构。

## 跨库摘要输出规则

`node`、`python`、`codex` 和 `workbuddy` 保持兼容性字段；新增 Agent CLI 只在本次被请求或实际检查时加入。
只传递状态、版本和阻塞类别，不传递用户名、路径、token、cookie、命令历史或配置内容。

固定 YAML 结构如下（不含秘密；字段不得增删）：

```yaml
schema_version: 2
checked_at: <RFC3339-with-timezone>
os: <macos|windows|linux|unknown>
arch: <architecture>
shell: <shell-or-unknown>
tools:
  node: {status: <ready|missing|update_available|blocked>, version: <version-or-null>}
  python: {status: <ready|missing|update_available|blocked>, version: <version-or-null>}
  codex: {status: <ready|needs_configuration|missing|update_available|blocked>, version: <version-or-null>}
  workbuddy: {status: <ready|needs_configuration|missing|update_available|blocked>, version: <version-or-null>}
  claude: {status: <ready|needs_configuration|missing|update_available|blocked>, version: <version-or-null>}
  qoder: {status: <ready|needs_configuration|missing|update_available|blocked>, version: <version-or-null>}
  antigravity: {status: <ready|needs_configuration|missing|update_available|blocked>, version: <version-or-null>}
  opencode: {status: <ready|needs_configuration|missing|update_available|blocked>, version: <version-or-null>}
  kimi: {status: <ready|needs_configuration|missing|update_available|blocked>, version: <version-or-null>}
  deepcode: {status: <ready|needs_configuration|missing|update_available|blocked>, version: <version-or-null>}
network: {status: <ready|degraded|blocked>, checked_sources: <count>}
blockers: []
next_handoff: <none|soia-env-open-skills-install|soia-open-skills|soia-private-skills>
```

## 权限与回滚

- 默认只读检查；安装由客户明确提出即视为目标授权，但每次新增管理员权限、系统范围安装、PATH/profile 修改仍需单独确认。
- 不使用 `sudo`、管理员终端、注册表、代理、DNS 或证书变更作为“顺手修复”。
- 安装失败时保留已安装状态，记录具体包/版本和回滚方式；不自动卸载、不覆盖现有版本。
- 远程登录和服务授权由客户在官方界面完成，Agent 不代填密码或验证码。

## 前向验收

用 fixture 模拟“Node 缺失、Python 已有、网络阻断”三种状态，确认编排结果只推进可用步骤，并将阻塞写入 `blockers`；真实安装必须另外验证官方二进制版本和客户可用的 GUI 登录状态。
