# Skill Authoring Spec

This public repository uses the same authoring principles as
`soia-open-skills`, with the `soia-env-` domain prefix.

## Required structure

```text
skills/<skill-name>/
├── SKILL.md
├── agents/openai.yaml
├── references/   # only when needed
└── scripts/      # only when deterministic code is needed
```

Start new skills from `templates/skill-template/` and keep each `SKILL.md`
under 500 lines. Do not add `README.md`, installation guides, changelogs, or
quick-reference files inside a skill directory.

## Frontmatter

```yaml
---
name: soia-env-example-install
description: Describe what the skill does and its trigger phrases.
version: 1.0.0
created_at: 2026-07-20 00:00:00
updated_at: 2026-07-20 00:00:00
created_by: <model-name>
updated_by: <model-name>
---
```

Use lowercase kebab-case names with four or five segments. New skills in this
repository normally start with `soia-env-` and a specific action/object pair.

## Customer-readable contract

Every skill must explain near the top:

- `客户可读说明`;
- `这个技能可以做什么`;
- `客户如何使用`;
- `依赖与安装` or equivalent;
- `日志与完成回执`.

The first screen must tell a beginner what they need to provide and what the
agent will do. State which actions are read-only and which change the machine.

## Safety and portability

- Never hardcode personal paths, accounts, secrets, or machine-specific
  defaults.
- Prefer official vendor sources. Keep source URLs and version facts in
  `references/` and label them with the date checked.
- Detect before changing. Use dry-run or a plan for PATH/profile changes,
  admin elevation, uninstall, and network settings.
- Never ask a customer to paste a secret into chat or terminal.
- Use `tempfile`, `Path.home()`, `os.tmpdir()`, and `pathlib`/`path.join` for
  script paths; do not add Unix-only hardcoded paths.

## Validation

Static checks are not enough for installation skills. Add a fixture or forward
test that verifies structured output, and document a safe manual check. A
successful command exit is not proof that a tool is usable: verify the binary,
version, PATH, and a harmless operation separately.
