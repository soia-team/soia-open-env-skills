# 输出格式（客户状态列表 / 跨库摘要）

## 客户状态列表细则

- 只列客户要求的目标及其必要前置项，不把所有已安装工具全部展开。
- `更新时间` 是该行完成最终验证的时间，不是技能文件的修改时间。
- 网络诊断的版本列写“不适用”；无法取得软件最新版本时写“未取得”。
- 内部依赖检查正常时不单独成行；只有它阻塞目标时才增加前置项行。
- 机器可读 YAML/JSON 摘要在客户列表之后提供，并保持下方固定结构。

## 跨库摘要格式

输出不含秘密的 YAML 或 JSON 摘要，字段固定为：

```yaml
schema_version: 2
checked_at: <RFC3339-with-timezone>
os: <macos|windows|linux|unknown>
arch: <architecture>
shell: <shell-or-unknown>
tools:
  node: {status: <ready|missing|update_available|blocked>, version: <version-or-null>}
  python: {status: <ready|missing|update_available|blocked>, version: <version-or-null>}
  codex: {status: <ready|needs_configuration|missing|update_available|blocked>, version: <version-or-null>}
  workbuddy: {status: <ready|needs_configuration|missing|update_available|blocked>, version: <version-or-null>}
  claude: {status: <ready|needs_configuration|missing|update_available|blocked>, version: <version-or-null>}
  qoder: {status: <ready|needs_configuration|missing|update_available|blocked>, version: <version-or-null>}
  antigravity: {status: <ready|needs_configuration|missing|update_available|blocked>, version: <version-or-null>}
  opencode: {status: <ready|needs_configuration|missing|update_available|blocked>, version: <version-or-null>}
  kimi: {status: <ready|needs_configuration|missing|update_available|blocked>, version: <version-or-null>}
  deepcode: {status: <ready|needs_configuration|missing|update_available|blocked>, version: <version-or-null>}
network: {status: <ready|degraded|blocked>, checked_sources: <count>}
blockers: []
next_handoff: <none|soia-env-open-skills-install|soia-open-skills|soia-private-skills>
```

`node`、`python`、`codex` 和 `workbuddy` 保持兼容性字段；新增 Agent CLI 只在本次被请求或实际检查时加入。只传递状态、版本和阻塞类别，不传递用户名、路径、token、cookie、命令历史或配置内容。
