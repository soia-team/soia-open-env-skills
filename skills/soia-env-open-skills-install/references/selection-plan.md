# Install selection / plan handoff schema

`scripts/plan_install.py` 生成只读、机器可消费的 selection plan；它不执行安装，不写用户 state，也不复制 `soia-meta` 实现。调用方可以把同形 JSON 作为输入。

## 输入

```json
{
  "scope": "project",
  "agents": ["codex"],
  "target": {"kind": "skill", "name": "soia-env-open-skills-install"},
  "confirmed": false
}
```

- `scope`: `project` 或 `global`，缺失即 `selection_required`。
- `agents`: `claude`、`codex`、`workbuddy` 的列表；`"*"` 只在客户明确选择全宿主时使用，缺失即 `selection_required`。
- `target.kind`: `skill`、`domain` 或 `all`；前两者需要 `target.name`，缺失即 `selection_required`。
- `confirmed`: 只表示调用方已确认计划；计划脚本仍然 `plan_only`，不安装。

## 输出

```json
{
  "schema_version": 1,
  "scope": "project",
  "agents": ["codex"],
  "target": {"kind": "skill", "name": "soia-env-open-skills-install"},
  "target_kind": "skill",
  "target_name": "soia-env-open-skills-install",
  "selection_required": false,
  "pending": true,
  "pending_reason": ["explicit confirmation required before installation"],
  "state": "confirmation_required",
  "confirmed": false,
  "dry_run": true,
  "plan_only": true,
  "matrix": [{"scope": "project", "agent": "codex", "target_kind": "skill", "target_name": "soia-env-open-skills-install", "capability": "supported", "status": "planned"}]
}
```

没有 scope、agent 或 target 时，必须返回 `selection_required: true`、`pending: true`、`state: selection_required`，不能静默展开全部宿主或全部域。已选范围但未确认时是 `confirmation_required`。能力不支持或尚需宿主能力核查时，矩阵逐项标为 `blocked`，不可伪称可安装。
