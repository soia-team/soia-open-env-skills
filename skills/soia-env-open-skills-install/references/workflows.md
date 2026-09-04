# 阶段命令与回执细则

本文件是旧路径的兼容入口。请先读取 [SKILL.md](../SKILL.md)，再按 [selection-plan.md](selection-plan.md) 生成选择计划；不再把缺省宿主或粒度解释为全量。

只读：

```bash
python3 scripts/inspect_soia_plugins.py --json
python3 scripts/plan_install.py --scope project --agents codex --target-kind skill --target-name <skill-name>
```

确认后的宿主命令见 [official-sources.md](official-sources.md)，宿主项目/用户级差异见 [capabilities.md](capabilities.md)。安装后重新 inspect，回执使用实际验证后的 `checked_at`。
