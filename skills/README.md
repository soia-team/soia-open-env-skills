# SOIA Open Skills Catalog

> Generated from `skills/*/SKILL.md` and optional `agents/openai.yaml`.
> Do not edit by hand. Run `python3 scripts/generate_skill_catalog.py`.
> Discoverable by `npx skills add soia-team/soia-open-env-tools-skills -l`: 7 skills.

## Source Fields

- `SKILL.md` is the canonical cross-agent instruction file. Capabilities, dependencies, setup, workflow steps, logs, and completion summaries must live there.
- `agents/openai.yaml` is optional UI/catalog metadata for OpenAI/Codex-style surfaces and SOIA registry display: `display_name`, `short_description`, and `default_prompt`.
- Claude Code and generic skills.sh-compatible agents must be assumed to consume `SKILL.md`; do not put required workflow steps only in `agents/openai.yaml`.
- Legacy `metadata.json` files are not used to generate this catalog.

## Environment

| Skill | Description | Default Prompt |
|---|---|---|
| [`soia-env-codex-install`](./soia-env-codex-install/) | Install and verify OpenAI Codex CLI. | Install Codex for me and verify login. |
| [`soia-env-codex-setup-support`](./soia-env-codex-setup-support/) | Check the ChatGPT desktop app's Codex capability and CLI. | Check ChatGPT/Codex desktop and CLI, then diagnose failures. |
| [`soia-env-environment-setup`](./soia-env-environment-setup/) | Plan and coordinate beginner-friendly environment setup. | Help me set up this computer for development. |
| [`soia-env-network-diagnose`](./soia-env-network-diagnose/) | Diagnose network access before installing tools. | Check why downloads or package installs fail. |
| [`soia-env-node-install`](./soia-env-node-install/) | Install and verify Node.js and npm. | Install Node.js and npm for my project. |
| [`soia-env-python-install`](./soia-env-python-install/) | Install and verify Python and pip. | Install Python and make pip work. |
| [`soia-env-workbuddy-install`](./soia-env-workbuddy-install/) | Install and verify the WorkBuddy desktop app. | Install WorkBuddy without making me use a terminal. |

## Registry Export

Generate v7 SOIA registry manifests from the same sources when needed:

```bash
python3 scripts/generate_skill_catalog.py --registry-out <soia-repo>/runtime/registry/skills
```
