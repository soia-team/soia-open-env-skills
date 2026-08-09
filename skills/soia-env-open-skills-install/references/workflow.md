# 工作流细则（自然语言触发示例 / 阶段 0-5 / 状态回执取值）

## 客户如何使用（自然语言示例）

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

## 标准流程（阶段 0-5）

### 阶段 0 · 检查（只读，不改动机器）

```bash
python3 scripts/inspect_soia_plugins.py --json
```

输出各宿主可用性、市场接入状态、已安装插件版本。

### 阶段 1 · 确认安装计划

根据客户意图计算目标宿主 × 目标域的安装/更新矩阵，展示后等客户确认。判断规则：

- **宿主**：未指定宿主时检测全部可用宿主；指定「Codex」「Claude Code」「WorkBuddy」时只操作该宿主。
- **粒度**：「所有 SOIA 技能/插件」→ 全 8 域；「soia-dev」→ 单域；「某个技能」→ 找到所属域 → 单域。
- **动作**：插件未安装 → install；已安装 → update（并展示当前版本和最新版本）。

### 阶段 2 · Claude Code 安装/更新

```bash
# 市场未接入时先接入
claude plugin marketplace add soia-team/soia-open-skills

# 未安装的域：install
claude plugin install <域名>@soia

# 已安装的域：update
claude plugin update <域名>@soia
```

逐域执行，任一域失败记录并继续；每域完成后用 `plugin list` 核对版本。

### 阶段 3 · Codex 安装/更新

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

### 阶段 4 · WorkBuddy 专家安装/更新

```bash
# dry-run 先看计划
python3 <soia-open-skills>/skills/soia-meta-skill-release/scripts/install_workbuddy_experts.py \
  --dry-run [<域名>]

# 确认后执行（无参数装全部，传域名只装指定域）
python3 <soia-open-skills>/skills/soia-meta-skill-release/scripts/install_workbuddy_experts.py \
  [<域名>]
```

完成后必须提示客户**重启 WorkBuddy**，否则新专家不显示。`<soia-open-skills>` 路径通过 `SOIA_SKILL_REPOS_ROOT` 环境变量或 `--repo-dir` 参数解析；两者都没有时提示客户指定路径。

### 阶段 5 · 收尾验证

```bash
python3 scripts/inspect_soia_plugins.py --json
```

对比安装前后状态，输出域级回执表。

## 状态回执取值规则

- 宿主不可用：写「跳过（宿主不可用）」，不写「失败」
- 已有版本未变：写「已是最新 <版本>」
- 首次安装：写「已安装 <版本>」
- 更新：写「已更新 <旧版本> → <新版本>」
- `更新时间` 在该域最终验证后实时生成，格式 RFC3339 带时区
