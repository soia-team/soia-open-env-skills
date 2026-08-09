---
name: soia-env-open-skills-install
description: 在 Claude Code、Codex、WorkBuddy 上安装或更新 SOIA 开源技能，支持全部/单插件/单技能粒度与指定宿主。触发：「装好所有 SOIA 插件」「在 Codex 下装 SOIA」「更新 soia-dev 插件」。
dependencies:
  optional: [soia-env-claude-cli-install, soia-env-codex-install, soia-env-workbuddy-install, soia-env-network-diagnose]
version: 1.0.3
created_at: 2026-08-01 15:47:43
updated_at: 2026-08-09 01:40:00
created_by: claude sonnet 4.6
updated_by: deepseek-v4-flash
---

# soia-env-open-skills-install

把 SOIA 开源技能装到位，或把已有安装更新到最新版。支持三种粒度 × 任意宿主组合，一条指令覆盖从「全量初装」到「单个技能升级」的全部场景。

与 `soia-meta-skill-release` 的分工：本技能面向**用户视角的安装/更新**；skill-release 面向**维护者发布后的 sha pin 刷新、旧名清理、lock 对账**。WorkBuddy 脚本两者共用，但调用时机不同。

## 客户可读说明

### 这个技能可以做什么

| 客户想要 | 技能会做 | 客户能看到 |
|---|---|---|
| 全量装好所有 SOIA 技能 / 插件 | 接入市场 → 安装全部 8 个域插件 → 三宿主 | 每宿主安装计划与域级回执 |
| 在指定宿主装全部 SOIA 技能 | 只操作目标宿主，跳过其余 | 单宿主域级回执 |
| 装或更新某个域插件（如 soia-dev） | `plugin install / plugin update` 该域 | 该域在各宿主的前后版本对比 |
| 更新某个域插件下的单个技能 | 更新整个插件（技能以插件为交付单元）+ 说明哪个技能已更新 | 插件级更新 + 技能变更说明 |
| 检查当前安装状态，不改动机器 | 列出各宿主市场状态与已安装插件版本 | 三宿主三列状态表 |

> **粒度说明**：SOIA 以「域插件」为最小交付单元（如 `soia-dev@soia` 含 9 个技能）。「更新单个技能」在插件模式下等价于更新整个域插件，但技能会说明是哪个技能触发了更新。若需要真正按技能粒度安装（不安装同域其他技能），必须改用 `npx skills add` 路线——技能会提示该路线与插件路线互斥，让客户选择。

### 客户如何使用

完整自然语言示例表（10 条：全量/单域/单技能 × 三宿主，含「只查看当前状态」）见 [user-phrases.md](references/user-phrases.md)。执行任何安装/更新前都展示计划并等客户确认；没有得到明确同意前不改动机器。

### 依赖与安装

| 依赖 | 类型 | 缺失时怎么处理 |
|---|---|---|
| `claude` CLI | 按宿主 | 跳过 Claude 宿主，建议调 `soia-env-claude-cli-install` |
| `codex` CLI | 按宿主 | 跳过 Codex 宿主，建议调 `soia-env-codex-install` |
| WorkBuddy | 按宿主 | 跳过 WorkBuddy，建议调 `soia-env-workbuddy-install` |
| Python 3 | WorkBuddy 步骤 | 跳过 WorkBuddy 专家安装并说明 |
| `soia-meta-skill-release` 脚本 | WorkBuddy 步骤 | 跳过 WorkBuddy 专家安装并给出路径说明 |
| 网络诊断 | 可选前置 | 市场接入失败时调 `soia-env-network-diagnose` |

本技能是 `soia-env-environment-setup` 的下游（环境就绪后的下一步），也可独立触发。8 个开源域插件（域仓、技能数、常驻成本）见 [plugins.md](references/plugins.md)。


装整个域（Claude Code 与 Codex 共用同一份域插件）：

```bash
claude plugin marketplace add soia-team/soia-open-skills
claude plugin install soia-env@soia
```

只装本技能：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-open-skills-install -y
```

### 私密信息与中间数据

- 不读取、不存储任何凭据；只读检查不落盘；安装阶段脱敏进度写入 `~/.local/state/soia-skills/soia-env-open-skills-install/`；不将本地路径或用户名写入仓库。

### 日志与完成回执

最终输出：宿主可用性列表 + 域安装回执表 + 失败域的可重试命令 + WorkBuddy 重启提示（如有）。

## 标准流程

装整个域（Claude Code 与 Codex 共用同一份域插件）：

```bash
claude plugin marketplace add soia-team/soia-open-skills
claude plugin install soia-env@soia
```

只装这一个技能：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-open-skills-install -y
```

### 阶段 0 · 检查（只读，不改动机器）

```bash
python3 scripts/inspect_soia_plugins.py --json
```

输出各宿主可用性、市场接入状态、已安装插件版本。

### 阶段 1 · 确认安装计划

根据客户意图计算目标宿主 × 目标域的安装/更新矩阵，展示后等客户确认。判断规则：**宿主**未指定时检测全部可用宿主；**粒度**「所有 SOIA 技能/插件」→ 全 8 域、「soia-dev」→ 单域、「某个技能」→ 找到所属域 → 单域；**动作**插件未安装 → install、已安装 → update（并展示当前版本和最新版本）。

### 阶段 2 · Claude Code 安装/更新

市场未接入时先接入（命令见上方「装整个域」块），随后逐域执行：未安装的域 `claude plugin install <域名>@soia`，已安装的域 `claude plugin update <域名>@soia`；任一域失败记录并继续，每域完成后用 `plugin list` 核对版本。

### 阶段 3 · Codex 安装/更新

市场暂存必须刷新，否则拿到旧缓存（已知约束：2026-07-27 实际踩过），随后 `codex plugin marketplace add soia-team/soia-open-skills`；未安装的域 `codex plugin add <域名>@soia`，已安装的域 `codex plugin remove + add`（Codex 无 update 命令）。完整命令见 [official-sources.md](references/official-sources.md)。

### 阶段 4 · WorkBuddy 专家安装/更新

dry-run 先看计划，确认后执行 `soia-open-skills` 的 `install_workbuddy_experts.py`（无参数装全部，传域名只装指定域）；路径通过 `SOIA_SKILL_REPOS_ROOT` 环境变量或 `--repo-dir` 参数解析，两者都没有时提示客户指定路径。完成后必须提示客户**重启 WorkBuddy**，否则新专家不显示。命令见 [official-sources.md](references/official-sources.md)。

### 阶段 5 · 收尾验证

```bash
python3 scripts/inspect_soia_plugins.py --json
```

对比安装前后状态，输出域级回执表。

## 状态回执（强制）

安装/更新结束后输出下表，每个目标域一行：

| 域 | Claude Code | Codex | WorkBuddy | 更新时间 | 备注 |
|---|---|---|---|---|---|
| soia-meta | 已安装 1.8.0 | 已安装 1.8.0 | — | 2026-08-01T10:00:00+08:00 | WorkBuddy 无该域专家 |
| soia-dev | 已安装 1.6.0 | 跳过（宿主不可用） | 已安装 | 2026-08-01T10:00:01+08:00 | — |

- 宿主不可用：写「跳过（宿主不可用）」，不写「失败」；已有版本未变：写「已是最新 <版本>」；首次安装：写「已安装 <版本>」；更新：写「已更新 <旧版本> → <新版本>」。
- `更新时间` 在该域最终验证后实时生成，格式 RFC3339 带时区。

## 关于「单个技能」粒度

插件模式下，技能以**域插件**为交付单元，不支持只装某个域内的单一技能：

- 客户要「更新 soia-dev 里的 soia-dev-coding-agent」→ 更新整个 `soia-dev` 插件 → 9 个技能全部升级
- 若客户真的只需要该单一技能（不想要同域其他 8 个）→ 告知需改用 `npx skills add` 路线，但 npx 路线与插件路线**互斥**（并存会产生双份索引各自漂移）→ 让客户明确选择

## 不负责什么

- **卸载与禁用**。客户要卸载或禁用插件时给出 `claude plugin uninstall/disable <域名>@soia`、`codex plugin remove <域名>@soia` 命令说明，由客户决定；本技能不主动执行卸载。
- **私有技能仓**。只覆盖开源市场 `soia-team/soia-open-skills` 的 8 个域插件；私有技能仓的接入不在范围，也不在本仓提及其安装方式。
- **发布收尾**。sha pin 刷新、旧名清理、lock 对账属维护者动作，由 `soia-meta-skill-release` 负责；客户说「发布技能」应路由到那边。

## 安装与更新的中间状态

改动机器时展示阶段列表，失败即停止当前宿主（不影响其他宿主）：

```text
checking → planning/waiting_confirmation → installing/updating → verifying → completed/failed/blocked
```

## 权限与回滚

- `claude plugin` 和 `codex plugin` 命令均为用户级操作，不需要管理员权限；WorkBuddy 脚本写入 `~/.workbuddy/plugins/marketplaces/my-experts/plugins`，不需要管理员权限。
- 失败时不自动回滚；给出对应的手动卸载命令供客户选择。

## 前向测试

- Mock `claude`/`codex`：未安装 / 已安装无市场 / 已接入市场各场景；验证「跳过不可用宿主」不影响其他宿主，验证「指定单宿主」只操作该宿主。
- 验证「指定单域」只安装/更新该域；「已是最新版」不触发重复安装（update 输出 already at latest 时记「已是最新」）；「单个技能触发」找到所属域并更新整个插件。
- 验证 WorkBuddy 脚本路径缺失时给出明确提示而非异常退出；验证 `更新时间` 在验证后生成、非硬编码。
