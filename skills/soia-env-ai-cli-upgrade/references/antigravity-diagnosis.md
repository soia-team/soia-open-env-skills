# Antigravity diagnosis


Use non-sensitive checks first:

```bash
type -a agy || true
agy --version
agy models
DRY_RUN=1 TOOLS="agy" \
  bash skills/soia-env-ai-cli-upgrade/scripts/upgrade-ai-clis.sh
```

`agy models` is a model-list discovery request, not a model prompt. Its output
is scoped to the authenticated account, plan, and current service state; do not
hardcode its count, order, display names, aliases, or a default model. If it
requires browser interaction, return `blocked_user_action`. Do not use
`agy -p` as an auth or model-list check because that is a real model call and
may consume quota or credits.

On macOS, source verification can also inspect the installed executable without
reading authentication state:

```bash
agy_bin="$(command -v agy)"
file "$agy_bin"
codesign -dv --verbose=4 "$agy_bin" 2>&1
spctl -a -vv -t execute "$agy_bin"
```

Compare the signing identity, executable architecture, and current release with
Google's [official repository](https://github.com/google-antigravity/antigravity-cli)
and [CLI documentation](https://antigravity.google/docs/cli-overview). Do not
hardcode a release version or checksum in this public skill.
