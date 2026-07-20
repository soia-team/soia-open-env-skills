# 清理安全合同

## 目录

- 受管根目录
- 状态清理标记
- 计划合同
- 授权合同
- 执行与复核合同

## 受管根目录

执行器只接受解析器返回的 `config`、`state`、`cache` 和 `temp` 根目录。环境变量只允许改变这些根目录的位置，不能增加第五类目录。配置根目录永远不产生删除候选。

环境变量覆盖的自定义根目录必须先存在 `.soia-storage-root.json`：

```json
{
  "schema_version": 1,
  "managed_by": "soia-skills",
  "root_kind": "cache"
}
```

`root_kind` 必须与被覆盖的根目录类别精确一致。缺少标记时，执行器拒绝把任意目录认领为 SOIA 存储。创建这个标记本身属于配置变更，Agent 必须先向客户展示目标目录和影响并取得确认。

清理目标必须是对应根目录的后代普通文件。执行器逐项拒绝根目录自身、符号链接、符号链接祖先、非普通文件、安全标记和活动目录。`.soia-storage-root.json` 本身永不删除。

## 状态清理标记

state 默认只统计。某个技能希望允许轮换脱敏审计状态时，必须在该技能 state 目录放置：

```text
.soia-managed-storage.json
```

最小格式：

```json
{
  "schema_version": 1,
  "owner_skill": "soia-env-example",
  "data_class": "audit_state",
  "retention_days": 30,
  "cleanup_allowed": true
}
```

执行器使用全局 `state_days` 与标记 `retention_days` 中较大的值。默认每个标记目录同时限制为 100 个普通文件和 10 MiB，超过时按最旧顺序生成高风险候选。标记缺失、格式错误、owner 不是 `soia-` 技能、类别不在白名单或 `cleanup_allowed` 不为 `true` 时，不产生 state 删除候选。

计划保存标记文件的 SHA-256。执行前标记变化会使对应候选失效。标记本身永不删除。

## 计划合同

计划至少包含：

```yaml
schema_version: 1
plan_id: <unique-id>
created_at: <RFC3339-with-timezone>
expires_at: <created-at-plus-30-minutes>
authorization_required: true
roots: <resolved-managed-roots>
policy: <retention-and-capacity-policy>
summary: <per-class-size-and-candidate-count>
candidates: <exact-regular-file-metadata>
plan_digest: <sha256-of-canonical-plan>
```

计划必须写在受管 state 根目录内，使用私有权限且不得覆盖既有文件。候选保存 `size` 和 `mtime_ns`；执行前任一值变化都应跳过，不能重新解释为“仍然差不多”。

## 授权合同

客户初始提出“清理”只授权生成计划，不授权删除未知候选。Agent 必须：

1. 展示计划摘要和不可逆风险；
2. 等待客户在新回复中明确确认当前 `plan_id`；
3. 生成随机、不含客户原话的 `authorization_id`；
4. 把客户确认的当前 `plan_id` 作为 `confirmed_plan_id` 提交；
5. 记录带时区 `authorized_at`；
6. 同时提交原始 `plan_digest` 和固定风险确认常量。

执行器拒绝客户确认的计划编号不匹配、授权早于计划、授权时间在未来、计划超过 30 分钟、摘要不匹配、授权 ID 格式错误或缺少固定风险确认常量的请求。

## 执行与复核合同

执行器逐文件重新验证根目录、文件类型、符号链接、活动标记、大小、修改时间、时效和状态标记。单项失败时记录 `skipped`，不得扩大删除范围或改用递归强制删除。

只用普通文件 `unlink` 删除已授权候选；随后只尝试删除这些文件的空父目录，且不能删除受管根目录。禁止使用对未知路径的 `rm -rf`、通配符删除或跟随符号链接。

回执必须记录：

```yaml
schema_version: 1
status: <completed-or-completed_with_skips>
plan_id: <plan-id>
confirmed_plan_id: <customer-confirmed-plan-id>
plan_digest: <plan-digest>
authorization_id: <opaque-id>
authorized_at: <RFC3339-with-timezone>
checked_at: <RFC3339-with-timezone>
deleted_files: <count>
deleted_bytes: <bytes>
skipped: <fail-closed-results>
disk_free_before: <bytes>
disk_free_after: <bytes>
receipt_digest: <sha256>
```

`verify` 必须重新校验回执摘要，并检查已删除路径是否重新出现。客户可见总结只显示类别、数量、大小和状态；精确路径留在本机私有回执中。
