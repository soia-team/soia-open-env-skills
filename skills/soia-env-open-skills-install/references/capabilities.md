# 宿主与范围能力矩阵

这是安装前的能力边界，不是安装授权。命令使用前仍需读取当前 CLI 的 `--help` 或官方来源确认版本差异。

| 宿主 | project | global/user | 事实与降级 |
|---|---|---|---|
| Claude Code | 支持 `npx skills add` 项目技能，使用 agent/skill 选择 | `claude plugin install/update` 为用户级域插件；npx 也可全局 | 插件命令不能冒充项目级；目标是域/全量时先确认项目安装器能力 |
| Codex | 支持 `npx skills add` 项目技能，使用 agent/skill 选择 | `codex plugin add` 为用户级域插件；npx 也可全局 | Codex 没有 plugin update，更新走当前 help/官方确认的 remove+add 或可用更新路径 |
| WorkBuddy | 当前官方专家脚本写用户级专家目录，项目范围阻塞 | `install_workbuddy_experts.py` 支持 dry-run 后按域/全量 | 不把用户级专家目录称为项目安装；缺少脚本路径或权限时阻塞 |

已核实的 npx help（本次开发环境）：`skills add` 默认项目范围；`-g/--global` 是全局范围；`-a/--agent` 选择宿主；`-s/--skill` 选择技能。这里的 help 结果只证明参数存在，不证明目标机器的网络、登录或安装结果。

发布不会自动安装。项目/全局、单/多 Agent、单技能/整域/`*` 全量均保留，但默认推荐项目 + 单 Agent + 单技能；扩大范围要由客户明确选择、先出计划/安装矩阵并确认。
