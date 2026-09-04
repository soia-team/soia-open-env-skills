# 客户自然语言示例（完整表）

未指定范围、宿主或粒度时只返回 `selection_required`；以下安装例均需先生成矩阵并确认。`*` 全量是客户明确选择，不是默认值。

| 客户说 | 技能的理解 | 执行范围 |
|---|---|---|
| 「帮我装好所有 SOIA 技能」 | 全量安装，全宿主 | 8 域 × 3 宿主 |
| 「帮我装好所有 SOIA 插件」 | 全量安装，全宿主 | 8 域 × 3 宿主 |
| 「帮我在 Codex 下装好所有 SOIA 技能」 | 全量安装，Codex 宿主 | 8 域 × Codex |
| 「帮我在 Codex 下装好所有 SOIA 插件」 | 全量安装，Codex 宿主 | 8 域 × Codex |
| 「帮我在 Claude Code 下装好所有 SOIA 技能」 | 全量安装，Claude Code 宿主 | 8 域 × Claude Code |
| 「帮我更新 Claude Code 下所有 SOIA 插件」 | 全量更新，Claude Code 宿主 | 8 域 × Claude Code |
| 「帮我更新 Claude Code 下 soia-dev 插件」 | 单域更新，Claude Code 宿主 | soia-dev × Claude Code |
| 「帮我在项目里的 Codex 下装 soia-env-open-skills-install」 | 项目单技能 | 该项目 × Codex × 单技能 |
| 「帮我更新 Claude Code 下 soia-dev 里的 soia-dev-coding-agent 技能」 | 用户级单技能触发，更新整个域插件 | soia-dev × Claude Code |
| 「帮我在 WorkBuddy 里装好所有 SOIA 专家」 | 全量安装，WorkBuddy 宿主 | 8 域 × WorkBuddy |
| 「只查看当前状态，不安装」 | 只读检查 | 3 宿主全查，不改动 |

执行任何安装/更新前都展示计划并等客户确认；没有得到明确同意前不改动机器。
