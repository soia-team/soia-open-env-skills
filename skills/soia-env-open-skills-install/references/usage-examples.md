# 客户如何选择范围

未指定范围、宿主或粒度时，先返回 `selection_required`，不要检测全部并执行全量。以下都是明确选择后的计划示例：

| 客户说 | scope | agents | target |
|---|---|---|---|
| “在这个项目给 Codex 装 `soia-env-open-skills-install`” | project | codex | skill |
| “全局给 Claude Code 更新 `soia-env`” | global | claude | domain |
| “给 Codex 和 Claude Code 安装这个域” | global/project 待确认 | codex, claude | domain |
| “所有宿主装所有 SOIA 技能” | global | `*` | all |
| “只查看当前状态，不安装” | 不适用 | inspect all hosts | inspect only |

最后一行是只读检查，不需要安装确认；其他安装/更新请求都必须先出矩阵、等待确认。插件模式下域插件是交付单元；项目单技能优先使用 npx project 能力。能力差异见 [capabilities.md](capabilities.md)。
