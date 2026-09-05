# SOIA Skills Catalog

> Generated from `skills/*/SKILL.md` and optional `agents/openai.yaml`.
> Do not edit by hand. Run `python3 scripts/generate_skill_catalog.py`.
> Discoverable by `npx skills add soia-team/instruction-autonomy-20260905 -l`: 18 skills.

## Source Fields

- `SKILL.md` is the canonical cross-agent instruction file. Capabilities, dependencies, setup, workflow steps, logs, and completion summaries must live there.
- `agents/openai.yaml` is optional UI/catalog metadata for OpenAI/Codex-style surfaces and SOIA registry display: `display_name`, `short_description`, and `default_prompt`.
- Claude Code and generic skills.sh-compatible agents must be assumed to consume `SKILL.md`; do not put required workflow steps only in `agents/openai.yaml`.
- Legacy `metadata.json` files are not used to generate this catalog.

## Environment

| Skill | Description | Default Prompt |
|---|---|---|
| [`soia-env-ai-cli-upgrade`](./soia-env-ai-cli-upgrade/) | Audit and upgrade AI CLIs, using agy for consumer Google login and Gemini only for supported non-consumer lanes. | Use soia-env-ai-cli-upgrade to audit or upgrade my AI CLIs; treat agy as the consumer Google-login successor and keep Gemini opt-in for supported enterprise, API Key, or Vertex lanes. |
| [`soia-env-antigravity-cli-install`](./soia-env-antigravity-cli-install/) | Install and verify Google Antigravity CLI (agy) | Use $soia-env-antigravity-cli-install to check or install Google Antigravity CLI, verify the actual ~/.gemini/antigravity-cli state, and guide first Google login without updating an existing installation unless I request the latest version. |
| [`soia-env-claude-cli-install`](./soia-env-claude-cli-install/) | Install and verify the standalone Claude Code CLI | Use $soia-env-claude-cli-install to check or install Claude Code CLI, distinguish an existing config from a missing first login, and guide official browser authentication without updating an existing installation unless I request the latest version. |
| [`soia-env-codex-install`](./soia-env-codex-install/) | Install and verify the standalone Codex CLI, separately from ChatGPT.app. | Check or install my standalone Codex CLI separately from ChatGPT.app; show version, installation method and directory, actual config status, and guide first login with codex --login. Do not update unless I explicitly ask for the latest version. |
| [`soia-env-codex-setup-support`](./soia-env-codex-setup-support/) | Check Codex desktop and CLI, including logs, SSD, and common failures. | Check or diagnose Codex desktop and CLI, including logs_2.sqlite write amplification and SSD health. |
| [`soia-env-deepcode-cli-install`](./soia-env-deepcode-cli-install/) | Install and verify the DeepSeek-focused Deep Code CLI | Use $soia-env-deepcode-cli-install to check or install Deep Code CLI, verify ~/.deepcode/settings.json, guide DeepSeek API key setup, and run a real no-side-effect validation without updating an existing installation unless I request the latest version. |
| [`soia-env-environment-setup`](./soia-env-environment-setup/) | Plan and coordinate beginner-friendly environment setup. | Help me set up this computer for development. |
| [`soia-env-kimi-cli-install`](./soia-env-kimi-cli-install/) | Install and verify the standalone Kimi Code CLI | Use $soia-env-kimi-cli-install to check or install Kimi Code CLI, verify ~/.kimi-code/config.toml, and guide kimi login or /login without updating an existing installation unless I request the latest version. |
| [`soia-env-local-model-bench`](./soia-env-local-model-bench/) | Benchmark local LLMs on Apple Silicon: engine selection, download, deploy, 17-question eval, throughput and hardware profiling. | Use soia-env-local-model-bench to check my machine, help me pick an inference engine, then benchmark a local model and report comparable numbers. |
| [`soia-env-network-diagnose`](./soia-env-network-diagnose/) | Diagnose network access and local runtimes before installing AI tools. | Check why downloads or package installs fail, and what this machine can install. |
| [`soia-env-node-install`](./soia-env-node-install/) | Install and verify Node.js and npm. | Install Node.js and npm for my project. |
| [`soia-env-open-skills-install`](./soia-env-open-skills-install/) | 按确认范围安装 SOIA 技能；默认先生成项目级单技能计划。 | Use soia-env-open-skills-install to inspect hosts, build a project/global skill/domain/all plan, and wait for confirmation before any install. |
| [`soia-env-opencode-cli-install`](./soia-env-opencode-cli-install/) | Install and verify the standalone OpenCode CLI | Use $soia-env-opencode-cli-install to check or install OpenCode CLI, distinguish opencode.json from auth.json, and guide opencode auth login without updating an existing installation unless I request the latest version. |
| [`soia-env-pi-cli-install`](./soia-env-pi-cli-install/) | Install and verify the Pi (pi-coding-agent) CLI | Use $soia-env-pi-cli-install to check or install Pi CLI, verify ~/.pi/agent/settings.json, guide Provider credential setup, and run a real no-side-effect validation without updating an existing installation unless I request the latest version. |
| [`soia-env-python-install`](./soia-env-python-install/) | Install and verify Python and pip. | Install Python and make pip work. |
| [`soia-env-qoder-cli-install`](./soia-env-qoder-cli-install/) | Install and verify the standalone Qoder CLI | Use $soia-env-qoder-cli-install to check or install Qoder CLI, report whether ~/.qoder/settings.json is actually present, and guide qodercli /login without updating an existing installation unless I request the latest version. |
| [`soia-env-storage-cleanup`](./soia-env-storage-cleanup/) | 统计 SOIA 受管目录空间，并在客户明确授权后安全清理过期数据 | Use $soia-env-storage-cleanup to scan managed storage, show cleanup risks, and delete only after my explicit approval. |
| [`soia-env-workbuddy-install`](./soia-env-workbuddy-install/) | Install and verify the WorkBuddy desktop app. | Install WorkBuddy without making me use a terminal. |

## Registry Export

Generate v7 SOIA registry manifests from the same sources when needed:

```bash
python3 scripts/generate_skill_catalog.py --registry-out <soia-repo>/runtime/registry/skills
```
