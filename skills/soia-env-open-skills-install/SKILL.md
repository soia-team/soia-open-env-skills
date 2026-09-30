---
name: soia-env-open-skills-install
description: 按确认范围在 Claude Code、Codex、WorkBuddy 上安装或更新 SOIA 开源技能，默认项目级单技能。触发：「安装 SOIA 技能」「在 Codex 下装」「更新 soia-dev」
dependencies:
  optional: [soia-env-claude-cli-install, soia-env-codex-install, soia-env-workbuddy-install, soia-env-network-diagnose]
version: 1.1.4
created_at: 2026-08-01 15:47:43
updated_at: 2026-09-30 13:14:57
created_by: claude sonnet 4.6
updated_by: claude opus 5.5
---

# soia-env-open-skills-install

在客户确认的范围内安装或更新 SOIA 开源技能：`project`/`global`、单/多 Agent、`skill`/`domain`/`all` 都支持，默认建议项目 + 单 Agent + 单技能。发布不会自动安装。

## 客户可读说明

### 这个技能可以做什么

- 只读检查 Claude Code、Codex、WorkBuddy 的可用性、市场状态与当前安装。
- 生成机器可读的选择计划与 Agent × 范围 × 粒度矩阵。
- 确认后按当前 CLI/官方脚本安装或更新单技能、整域或全量，并验证实际结果。

### 客户如何使用

说明安装范围、宿主和粒度，例如“在这个项目给 Codex 装单个技能”“全局给 Claude Code 更新 `soia-dev`”。缺任一项时只检查并返回 `selection_required`，不默认全域。

### 依赖与安装

需要 Python 3 与对应宿主的官方 CLI 或 WorkBuddy 安装脚本；缺某个宿主只跳过它并报告，不改装其他宿主。宿主与范围的能力差异见[能力矩阵](references/capabilities.md)，域列表见[插件目录](references/plugins.md)。

安装本技能自身：仓库 `soia-team/soia-open-env-skills`，技能 `soia-env-open-skills-install`，域插件 `soia-env`。单技能用 `npx skills add`，整域用 `claude plugin install soia-env@soia` / `codex plugin add soia-env@soia`，WorkBuddy 用官方专家脚本；具体命令见[安装命令与宿主边界](references/official-sources.md)。只执行客户已确认的范围与宿主，读安装说明不等于执行安装。

### 私密信息与中间数据

只读取本次选择所需的 CLI 状态、市场状态和版本，不读取或打印凭据；只读检查与计划不落盘。获授权实际改动机器时，按仓库 `DATA_STORAGE_SPEC.md` 在技能 state 中记录脱敏阶段事件；临时输入放系统临时目录；仓库 checkout 不作运行时 state/cache/config。

### 日志与完成回执

状态区分 `inspection`、`selection_required`、`confirmation_required`、`blocked`、`installed`、`updated`；列实际宿主、范围、目标粒度、矩阵、版本与最终验证时间 `checked_at`，客户状态表另给验证后的 `更新时间`（RFC 3339，带时区）。计划或退出码不说成已安装；不打印账号、路径中的隐私部分或凭据。

## 核心流程

1. **检查（只读）。** `python3 scripts/inspect_soia_plugins.py --json` 确认宿主可用性与已安装状态；请求模糊不扩大范围。
2. **选择与计划。** 归一化 `scope`、`agents`、`target.kind/name`，运行 `python3 scripts/plan_install.py --scope <project|global> --agents <agent> --target-kind <skill|domain|all> --target-name <name>`（只读）。缺任一选择返回 `selection_required: true`；能力不支持逐项标 `blocked`。字段与输出见 [selection-plan](references/selection-plan.md)。
3. **确认门。** 展示 scope × Agent × target kind/name × action 矩阵、能力降级、影响范围与回滚路径。选择字段齐全不等于写入批准：没有客户对该计划的明确确认，不做任何安装、更新、市场接入、remove+add 或 WorkBuddy 写入。已展示影响并获明确批准、且含 source、具体 target、action 与删除/替换影响的完整计划，可由 find-skill、sync 或 release 传来直接执行，不重复询问；目标、宿主、粒度、source、action 或删除/替换影响有变时重新确认受影响部分。
4. **执行与验证。** 只调用 [official-sources](references/official-sources.md) 中已核实的命令，参数先用当前 `--help` 核对，不凭记忆发明项目级参数；证明不了能力就返回 `blocked` 或 `capability_check`。每个目标独立执行、独立验证版本或技能/专家实际存在，再汇总回执；失败不扩大范围、不自动回滚。WorkBuddy 完成后提示重启应用。

范围边界：用户级插件命令不能冒充项目安装；WorkBuddy 专家脚本只写用户级目录，项目范围一律 `blocked`；指定单宿主不波及其他宿主。机器变更阶段为 `checking → planning → waiting_confirmation → installing/updating → verifying → completed/failed/blocked`。

## 维护本技能时的验证

```bash
python3 scripts/plan_install.py --selftest
python3 scripts/inspect_soia_plugins.py --json
```

在仓库根另跑 `python3 -m unittest discover -s tests -p 'test_*.py'`。前向测试只用临时 JSON/fixture 与 mock，不执行真实安装；另以当前 `npx skills add --help` 核实项目范围不带 `-g`、支持 `--agent` 与 `--skill`。
