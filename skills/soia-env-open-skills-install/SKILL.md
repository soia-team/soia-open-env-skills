---
name: soia-env-open-skills-install
description: 在 Claude Code、Codex、WorkBuddy 上按确认范围安装或更新 SOIA 开源技能；默认项目级单技能，支持全局、整域和全量。触发：「安装 SOIA 技能」「在 Codex 下装」「更新 soia-dev」
dependencies:
  optional: [soia-env-claude-cli-install, soia-env-codex-install, soia-env-workbuddy-install, soia-env-network-diagnose]
version: 1.1.0
created_at: 2026-08-01 15:47:43
updated_at: 2026-09-04 17:16:01
created_by: claude sonnet 4.6
updated_by: gpt-5.6-luna
---

# soia-env-open-skills-install

在客户确认的范围内安装或更新 SOIA 开源技能。支持 `project`/`global`、单/多 Agent、`skill`/`domain`/`all`；默认建议项目、单 Agent、单技能。发布不会自动安装，但客户可以在发布后明确选择安装。

## 客户可读说明

### 这个技能可以做什么

- 只读检查 Claude Code、Codex、WorkBuddy 的可用性、市场状态和当前安装。
- 生成机器可读的选择计划与 Agent × 范围 × 粒度矩阵。
- 在确认后按当前 CLI/官方脚本安装或更新单技能、整域或全量，并验证实际结果。

### 客户如何使用

请明确说明安装范围、宿主和粒度，例如“在这个项目给 Codex 装单个技能”“全局给 Claude Code 更新 `soia-dev`”。范围、宿主或粒度任一缺失时只检查并返回 `selection_required`，先询问，不检测全部后默认全域执行。要扩大到全局、整域、多宿主或 `*` 全量，必须明确选择；先展示 dry-run/安装矩阵，再等待确认。

### 依赖与安装

本技能需要 Python 3 执行检查/计划和对应宿主的官方 CLI 或 WorkBuddy 安装脚本。Claude/Codex/WorkBuddy 的范围能力不同，见 [references/capabilities.md](references/capabilities.md)；域列表见 [references/plugins.md](references/plugins.md)。缺少宿主时只跳过该宿主并报告，不静默改装其他宿主。

计划命令只读、不安装：

```bash
python3 scripts/inspect_soia_plugins.py --json
python3 scripts/plan_install.py --scope project --agents codex --target-kind skill --target-name <skill-name>
```

### 私密信息与中间数据

只读取本次选择所需的 CLI 状态、市场状态和版本；不读取或打印凭据。只读检查和计划不落盘。获得授权并实际改动机器时，按 `DATA_STORAGE_SPEC.md` 在技能 state 中记录脱敏阶段事件；临时输入放 OS 临时目录；仓库 checkout 不作为运行时 state/cache/config。

### 日志与完成回执

回执区分 `inspection`、`selection_required`、`confirmation_required`、`blocked`、`installed` 和 `updated`，列出实际宿主、范围、目标粒度、矩阵、版本与最终验证时间 `checked_at`；面向客户的状态表同时给出验证后的 `更新时间`（RFC 3339，带时区）。不把计划或退出码说成已安装，不打印账号、路径中的隐私部分或凭据。

## 核心流程

1. **检查（只读）**：运行 `inspect_soia_plugins.py --json`，确认宿主可用性和已安装状态；不要因为请求模糊就扩大范围。
2. **选择与计划**：归一化 `scope`、`agents` 和 `target.kind/name`，运行 `plan_install.py`。缺任一选择返回 `selection_required: true`；能力不支持返回逐项 `blocked`。
3. **确认门**：展示 scope × Agent × target kind/name × action 的安装矩阵、能力降级、影响范围和回滚路径。没有客户对该计划的明确确认，不执行任何安装、更新、市场接入、remove+add 或 WorkBuddy 写入。
4. **执行与验证**：确认后只调用 [references/official-sources.md](references/official-sources.md) 中当前已核实的命令；项目级优先使用已验证的 npx project + agent/skill 选择，用户级域插件使用对应宿主命令。每个目标独立记录、验证版本/实际技能或专家存在性，再汇总回执；失败不扩大范围、不自动回滚。

## 能力与粒度边界

| 目标 | project | global/user |
|---|---|---|
| Claude Code / Codex 单技能 | npx project（不带 `-g`，参数由当前 help 确认） | npx global 或对应域插件 |
| Claude Code / Codex 整域/全量 | 需项目安装器能力检查，不能把用户级插件命令冒充项目安装 | 对应域插件或 npx 全量，仍需确认 |
| WorkBuddy 任意目标 | 当前专家脚本不支持项目目录，阻塞 | 官方专家脚本 dry-run 后按域/全量 |

项目、全局、单/多 Agent、单技能、整域和 `*` 全量都保留支持；默认不全量，范围不明必须询问。完整 handoff 字段见 [references/selection-plan.md](references/selection-plan.md)。

## 标准命令与收口

市场接入、Claude/Codex 插件、npx project/global 和 WorkBuddy 的具体命令与版本差异见 [references/official-sources.md](references/official-sources.md)。不凭记忆发明项目级参数；若 help/官方来源不能证明能力，返回 `blocked` 或 `capability_check`。

确认后的机器变更阶段为：`checking → planning → waiting_confirmation → installing/updating → verifying → completed/failed/blocked`。每个宿主只操作计划列出的目标；指定单宿主不会波及其他宿主。WorkBuddy 完成后提示重启应用。

## 前向验证

```bash
python3 scripts/plan_install.py --selftest
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/inspect_soia_plugins.py --json
```

前向测试使用临时 JSON/fixture 和 mock，不执行真实安装；另以当前 `npx skills add --help` 核实 project 不带 `-g`、`--agent`、`--skill` 能力。完整仓门禁还包括 catalog、audit 和 `git diff --check`。
