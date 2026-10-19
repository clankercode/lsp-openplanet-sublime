# Sublime LSP API research

Verified 2026-10-19 against released [LSP 2.16.0](https://github.com/sublimelsp/LSP/tree/4070-2.16.0), commit `b51e5d8` (full SHA in verification receipt). Current master was also inspected; it exposes the same integration API. Structural discovery used codebase-memory-mcp with exact source checks for `plugin/api.py`, `plugin/core/types.py`, `plugin/core/windows.py`, and transport/session behavior.

- `LspPlugin` is the supported helper base. `AbstractPlugin` is deprecated. Registration uses `register()` / `unregister()`; the top-level package directory supplies the session name and settings filename.
- `is_applicable_async(IsApplicableContext)` determines both session startup and document attachment. The package combines a file/syntax pairing check with LSP's ordinary scope/scheme check. This avoids attaching to every `source.toml` view.
- `on_pre_start_async(OnPreStartContext)` runs on LSP's worker thread; mutate `variables`, `workspace_folders`, or `working_directory`. Raise `PluginStartError` to explain failure. No subprocess or network work blocks Sublime's UI thread.
- `ClientConfig.root_settings` contains custom keys such as `server_path`; `ClientConfig` is not a dictionary. `initialization_options` is passed through untouched.
- `TransportConfig.resolve_launch_config` expands command arguments independently, without a shell. PATH settings are a prefix to the inherited PATH. List input is normalized before reaching LSP 2.16's transport.
- A workspace-capable server can reuse a session for loose files outside its initial root. `on_pre_send_notification_async` advertises additional loose-plugin roots before `didOpen` using `Session.update_folders`; explicit project folder choices are retained.
- LSP supports a TOML base scope/language identifier, and Sublime 4215 bundles TOML syntax. `.as` collides with built-in ActionScript; the package replaces that default on load without replacing a user-selected custom syntax.
- Sublime rejects mixed-version syntax inheritance. The included grammar uses `include: scope:source.c++`, not `extends`, validated in the editor after a red/green regression test.

Sources: [public API](https://github.com/sublimelsp/LSP/blob/4070-2.16.0/plugin/api.py), [config](https://github.com/sublimelsp/LSP/blob/4070-2.16.0/plugin/core/types.py), [launch](https://github.com/sublimelsp/LSP/blob/4070-2.16.0/plugin/core/transports.py), [sessions](https://github.com/sublimelsp/LSP/blob/4070-2.16.0/plugin/core/sessions.py), [helper registry](https://github.com/sublimelsp/repository).
