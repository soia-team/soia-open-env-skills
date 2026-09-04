# 安装操作边界

本文件是兼容入口；主选择和确认规则见 [SKILL.md](../SKILL.md)。任何宿主命令都只能执行已确认矩阵中的行。

- Claude Code/Codex 用户级域插件：按 [official-sources.md](official-sources.md) 的当前命令执行；不要称为项目安装。
- Claude Code/Codex 项目单技能：使用当前 `npx skills add --help` 已证明的 project 形式，并显式传已确认 Agent/技能。
- WorkBuddy：只支持用户级专家脚本；先 dry-run，项目范围标 capability gap 并阻塞。
- 每个目标单独验证；指定单宿主不触碰其他宿主，失败不扩大范围。

阶段：`checking → planning → waiting_confirmation → installing/updating → verifying → completed/failed/blocked`。只读检查和计划不写用户状态；真实机器变更按 DATA_STORAGE_SPEC 记录脱敏阶段事件。
