# 操作细则（登录验证 / 中间状态记录 / 自动更新边界 / 权限与回滚）

## 首次登录与真实配置验证

- `配置文件目录`只显示候选目录；技能必须同时读取 `config_status` 和 `config_file_status`，不能把默认路径当成“已配置”。
- 如果 `~/.claude` 或 `settings.json` 尚未创建，Agent 在客户选定的项目中启动 `claude`，由 Claude Code 展示官方登录选项；客户只在 Anthropic 官方页面或 Claude 官方应用完成授权。
- 如果客户选择 Anthropic API 方式，客户自行在 Anthropic Console 创建并保管 API key；Agent 只检查“存在/可认证”的结果，不接收、不回显密钥。
- 登录完成后重新运行 `claude doctor` 和技能检查脚本；没有完成浏览器授权时，处理结果必须写“等待首次登录”，不能写“运行正常”。

## 客户状态列表细则

- 用户只问 Claude Code CLI 时，不增加 Node.js、npm、Codex、Claude 桌面产品或其他技能行。
- `更新时间` 必须在最终验证后生成；安装目录和配置目录优先显示 `~` 相对路径，避免暴露用户名。
- 已更新后 `当前状态` 仍写“已安装”，更新结果只放在 `处理结果`。
- 发现多个 `claude` 时汇报当前登录 shell 实际生效的副本，并提示冲突；不删除其他副本。
- 无法取得最新版时写“未取得”；不得用缓存、记忆或其他产品版本代替。
- `config_status=未创建` 或 `config_file_status=未创建` 时，处理结果写“等待首次登录/配置”，并给出启动命令和官方授权方式；不得只打印一个不存在的路径。

## 安装与更新的中间状态

真正改变机器时，为本次运行生成随机 `run_id`，在每个实际阶段立即调用 `scripts/record_install_progress.py`，并同步展示阶段列表。只读检查不创建记录。

```text
checking → planning → [waiting_confirmation] → installing/updating → verifying → completed/failed/blocked
```

| 阶段 | 当前状态 | 更新时间 | 处理结果 |
|---|---|---|---|
| <检查/计划/等待确认/安装或更新/验证/完成或失败> | <进行中/等待/已完成/失败/被阻塞> | <RFC3339-with-timezone> | <脱敏结果> |

- 安装使用 `--action install`；更新使用 `--action update`。
- 只有客户明确要求最新版时，更新阶段才能传 `--customer-requested-latest`；记录器会拒绝未授权更新。
- 记录只保存固定 `result_code`、阶段和时间，不保存命令全文、账号、token、响应正文或客户私有绝对路径。

## 产品自动更新边界

- 本技能“默认不更新”是指 Agent 不调用安装器或更新器。Claude Code 产品自身可能启用自动更新，必须在状态说明中披露。
- 只读检查不得修改 `autoUpdates`、`DISABLE_AUTOUPDATER` 或任何配置。
- 客户明确要求关闭或开启产品自动更新时，先展示影响，再按官方设置修改并复核；该配置授权不等于本次更新授权。

## 权限与回滚

- 优先用户级安装，不默认使用 `sudo`。需要管理员权限、修改 shell profile、切换来源或覆盖现有命令时先展示计划并取得单独确认。
- 更新前记录旧版本和来源；失败时保留原安装，不自动卸载、降级、清理配置或关闭自动更新。
- 网络脚本和安装包只存于每次运行独立的系统临时目录，成功、失败或取消都清理。
