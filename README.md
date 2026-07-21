# soia-open-env-skills

> **定位**：给任何 AI 帮小白建立一套可用的基础开发环境——网络诊断、Node/Python、桌面工具和主流 Agent CLI 的安装、验证与更新，一步一步可跟做。进阶技能见 [soia-open-skills](https://github.com/soia-team/soia-open-skills)。


面向小白的 SOIA 环境工具技能库：先判断系统和网络状态，再用官方或明确标注的上游来源安装、配置和验证 Codex、Claude Code、Qoder、Antigravity、OpenCode、Kimi Code、Deep Code、WorkBuddy、Node.js、Python 等基础工具。

## 首版技能

- `soia-env-environment-setup`：从零规划环境，按依赖顺序编排网络、运行时和 AI 工具检查。
- `soia-env-network-diagnose`：只读检查 DNS、HTTPS、代理、证书和下载源可达性。
- `soia-env-codex-install`：安装并验证 OpenAI Codex CLI。
- `soia-env-claude-cli-install`：安装并验证 Anthropic Claude Code CLI。
- `soia-env-qoder-cli-install`：安装并验证 Qoder CLI。
- `soia-env-antigravity-cli-install`：安装并验证 Google Antigravity CLI（`agy`），并处理 Gemini CLI 迁移边界。
- `soia-env-opencode-cli-install`：安装并验证开源 OpenCode CLI。
- `soia-env-kimi-cli-install`：安装并验证 Moonshot AI Kimi Code CLI。
- `soia-env-deepcode-cli-install`：安装并验证面向 DeepSeek 优化的社区开源 Deep Code CLI（`lessweb/deepcode-cli`）。
- `soia-env-codex-setup-support`：安装和验证 ChatGPT 桌面应用中的 Codex 能力、CLI，并排查磁盘、网络、登录和工作区问题。
- `soia-env-workbuddy-install`：通过官方桌面安装包安装并验证 WorkBuddy。
- `soia-env-node-install`：安装并验证 Node.js、npm 和 PATH。
- `soia-env-python-install`：安装并验证 Python、pip 和虚拟环境。
- `soia-env-storage-cleanup`：统计 SOIA 受管目录空间，展示风险清单，并只在客户明确授权后清理过期缓存、临时文件和受管状态。

## 三个技能库如何配合

```text
soia-open-env-skills  →  环境可用性 / 工具安装 / 网络诊断
             ↓ readiness summary
soia-open-skills             →  云盘 / 知识库 / PKM 工作流
             ↓ optional handoff
soia-private-skills          →  私有 SOIA 治理、审计和内部执行
```

环境技能不复制其他仓库的技能，也不自动安装私有技能；它只输出可移植的
`checked_at / os / arch / shell / tool / version / status / blockers` 摘要，供后续技能判断前置条件。

## 安装

从远程仓库安装单个技能：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -s soia-env-environment-setup -y
```

安装全部技能：

```bash
npx skills add soia-team/soia-open-env-skills -g -a '*' -y
```

## 权限模型

- 仓库公开，`main` 受保护，改动通过 PR 合并。
- GitHub Actions 只读仓库内容并运行审计，不保存用户机器凭据。
- 技能默认只读探测；安装、PATH/profile 修改、管理员权限、网络设置变更和删除文件必须先展示计划并确认。
- 发现新版本时默认只汇报，不自动更新；只有客户明确说“更新到最新版本”或同等明确指令后才执行更新。模糊的“更新”先展示版本并询问。
- 真正执行安装或更新时，技能会在对话中持续显示检查、计划、执行、验证和完成/失败状态，并把脱敏阶段记录保存在用户私有 state 目录。
- 存储清理的初始请求只授权扫描和生成计划；客户必须在看到最新候选及不可逆风险后再次明确授权，才能执行删除。
- 客户不需要操作终端；浏览器登录、验证码、系统安全提示和第三方服务授权由客户在官方界面完成。
- 凭据、中间数据、缓存、状态和临时文件按
  [DATA_STORAGE_SPEC.md](./DATA_STORAGE_SPEC.md) 分层；普通配置文件不保存 secret。

## 开源来源

安装说明优先引用官方来源：

- Codex CLI：<https://help.openai.com/en/articles/11096431>
- Claude Code CLI：<https://docs.anthropic.com/en/docs/claude-code/getting-started>
- Qoder CLI：<https://docs.qoder.com/en/cli/quick-start>
- Google Antigravity CLI：<https://codelabs.developers.google.com/antigravity-cli-hands-on>
- OpenCode CLI：<https://opencode.ai/docs>
- Kimi Code CLI：<https://www.kimi.com/code/docs/kimi-code-cli/guides/getting-started>
- Deep Code CLI 上游：<https://github.com/lessweb/deepcode-cli>
- WorkBuddy：<https://www.workbuddy.cn/>
- Node.js：<https://nodejs.org/en>
- Python：<https://www.python.org/downloads/>

## 贡献与验证

参见 [CONTRIBUTING.md](./CONTRIBUTING.md)、[SKILL_SPEC.md](./SKILL_SPEC.md)、
[DATA_STORAGE_SPEC.md](./DATA_STORAGE_SPEC.md) 和 [AGENTS.md](./AGENTS.md)。提交前运行：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/generate_skill_catalog.py --check
python3 scripts/audit_skills.py
git diff --check
```
