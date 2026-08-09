# 客户如何使用（自然语言示例全表）

| 客户说 | 技能的理解 | 执行范围 |
|---|---|---|
| 「帮我装好所有 SOIA 技能」 | 全量安装，全宿主 | 8 域 × 3 宿主 |
| 「帮我装好所有 SOIA 插件」 | 全量安装，全宿主 | 8 域 × 3 宿主 |
| 「帮我在 Codex 下装好所有 SOIA 技能」 | 全量安装，Codex 宿主 | 8 域 × Codex |
| 「帮我在 Codex 下装好所有 SOIA 插件」 | 全量安装，Codex 宿主 | 8 域 × Codex |
| 「帮我在 Claude Code 下装好所有 SOIA 技能」 | 全量安装，Claude Code 宿主 | 8 域 × Claude Code |
| 「帮我更新 Claude Code 下所有 SOIA 插件」 | 全量更新，Claude Code 宿主 | 8 域 × Claude Code |
| 「帮我更新 Claude Code 下 soia-dev 插件」 | 单域更新，Claude Code 宿主 | soia-dev × Claude Code |
| 「帮我更新 Claude Code 下 soia-dev 里的 soia-dev-coding-agent 技能」 | 单技能触发，更新整个插件 | soia-dev × Claude Code |
| 「帮我在 WorkBuddy 里装好所有 SOIA 专家」 | 全量安装，WorkBuddy 宿主 | 8 域 × WorkBuddy |
| 「只查看当前状态，不安装」 | 只读检查 | 3 宿主全查，不改动 |

## 关于「单个技能」粒度

插件模式下，技能以**域插件**为交付单元，不支持只装某个域内的单一技能：

- 客户要「更新 soia-dev 里的 soia-dev-coding-agent」→ 更新整个 `soia-dev` 插件 → 9 个技能全部升级
- 若客户真的只需要该单一技能（不想要同域其他 8 个）→ 告知需改用 `npx skills add` 路线，但 npx 路线与插件路线**互斥**（并存会产生双份索引各自漂移）→ 让客户明确选择
