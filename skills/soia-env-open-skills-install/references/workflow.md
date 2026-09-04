# 工作流细则

主流程和安装选择的唯一入口是 [SKILL.md](../SKILL.md)。本文件保留为兼容链接，避免旧调用方继续读取过时的“未指定即全量”规则。

1. 运行 `scripts/inspect_soia_plugins.py --json`，只读检查。
2. 运行 `scripts/plan_install.py`，选择 `project|global`、一个或多个 Agent、`skill|domain|all` 和目标名。
3. 缺少任一选择返回 `selection_required`，不检测全部后默认安装。
4. 展示计划矩阵并等待客户确认；确认后只执行计划目标，完成后再次 inspect 验证。

能力差异与命令来源见 [capabilities.md](capabilities.md) 和 [official-sources.md](official-sources.md)；机器可读 handoff 字段见 [selection-plan.md](selection-plan.md)。
