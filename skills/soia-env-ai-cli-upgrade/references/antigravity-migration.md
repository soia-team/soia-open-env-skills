# Gemini consumer migration and Antigravity authentication


These are two separate executables and authentication products. `agy` replaces
Gemini CLI only for the consumer **Login with Google** path; it is not a 1:1
command alias. Keep `gemini` coverage for supported non-consumer lanes, but do
not reinstall or upgrade it in the default batch. Never alias `gemini` to
`agy`, delete Gemini CLI without explicit authorization, or silently move an
account or billing channel.

- Since June 18, 2026, Gemini Code Assist consumer accounts can no longer use
  **Sign in with Google** in Gemini CLI. Google directs consumer users to
  Antigravity. Re-check the current [Google deprecation notice](https://developers.google.com/gemini-code-assist/docs/deprecations/code-assist-individuals)
  and [migration guide](https://antigravity.google/docs/gcli-migration) before
  acting.
- Gemini Code Assist Standard and Enterprise remain supported in Gemini CLI.
  Gemini API-key and Vertex AI authentication are also separate supported lanes;
  preserve them and follow the current [Gemini CLI authentication guide](https://github.com/google-gemini/gemini-cli/blob/main/docs/get-started/authentication.mdx).
- Antigravity CLI uses the system keyring when a session is available and falls
  back to Google Sign-In. The batch upgrade script does not inspect the keyring,
  open a browser, read auth files, or send a model prompt.

After installation, launch `agy` in a PTY only when the user explicitly asked to
log in. If a browser, account chooser, consent screen, paid-credit choice, or
first-launch migration checklist appears, return `blocked_user_action` and wait
for the user. Do not log OAuth URLs, state values, cookies, tokens, account ids,
or credential-file contents. A successful `agy --version` proves only that the
binary runs; it does not prove authentication.

`agy plugin import gemini` writes migrated plugin configuration. Run it only
after the user reviews and approves that separate migration action.
