# 操作细则（阶段命令 / 前向测试）

## 阶段 2 · Claude Code 安装/更新

```bash
# 市场未接入时先接入
claude plugin marketplace add soia-team/soia-open-skills

# 未安装的域：install
claude plugin install <域名>@soia

# 已安装的域：update
claude plugin update <域名>@soia
```

逐域执行，任一域失败记录并继续；每域完成后用 `plugin list` 核对版本。

## 阶段 3 · Codex 安装/更新

```bash
# 市场暂存必须刷新，否则拿到旧缓存（已知约束：2026-07-27 实际踩过）
rm -rf ~/.codex/.tmp/marketplaces/soia
codex plugin marketplace add soia-team/soia-open-skills

# 未安装的域：add
codex plugin add <域名>@soia

# 已安装的域：remove + add（Codex 无 update 命令）
codex plugin remove <域名>@soia
codex plugin add <域名>@soia
```

## 阶段 4 · WorkBuddy 专家安装/更新

```bash
# dry-run 先看计划
python3 <soia-open-skills>/skills/soia-meta-skill-release/scripts/install_workbuddy_experts.py \
  --dry-run [<域名>]

# 确认后执行（无参数装全部，传域名只装指定域）
python3 <soia-open-skills>/skills/soia-meta-skill-release/scripts/install_workbuddy_experts.py \
  [<域名>]
```

完成后必须提示客户**重启 WorkBuddy**，否则新专家不显示。`<soia-open-skills>` 路径通过 `SOIA_SKILL_REPOS_ROOT` 环境变量或 `--repo-dir` 参数解析；两者都没有时提示客户指定路径。

## 阶段 5 · 收尾验证

安装/更新结束后重新执行 `python3 scripts/inspect_soia_plugins.py --json`，对比安装前后状态，输出域级回执表。

## 前向测试

- Mock `claude`/`codex`：未安装 / 已安装无市场 / 已接入市场各场景
- 验证「跳过不可用宿主」不影响其他宿主
- 验证「指定单宿主」只操作该宿主
- 验证「指定单域」只安装/更新该域
- 验证「已是最新版」不触发重复安装（update 输出 already at latest 时记「已是最新」）
- 验证「单个技能触发」找到所属域并更新整个插件
- 验证 WorkBuddy 脚本路径缺失时给出明确提示而非异常退出
- 验证 `更新时间` 在验证后生成、非硬编码
