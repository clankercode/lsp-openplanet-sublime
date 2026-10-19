# LSP-openplanet for Sublime Text

Openplanet AngelScript language support through [LSP](https://lsp.sublimetext.io/) and [openplanet-lsp](https://github.com/clankercode/lsp-openplanet): completions, diagnostics, hover, signatures, definitions, references, rename, and semantic highlighting where the server supports them.

![Real Sublime Text diagnostics](docs/assets/sublime-diagnostics.png)

Actual Sublime Text 4 running the original example in [`examples/diagnostics`](examples/diagnostics). The misspelled `mesage` is intentional; the diagnostic comes from openplanet-lsp. See [verification](docs/verification.md) for versions, evidence, and limits.

## Install

Requires **Sublime Text 4 build 4200+** and **LSP 2.16+**. Sublime Text is a separately licensed product; this package is free.

1. Install **LSP** using Package Control. Recent Sublime builds include TOML syntax. If `info.toml` opens as Plain Text, install **TOML** or select TOML from the syntax menu.
2. Until the registry submission is accepted, use **Preferences → Browse Packages…**, then clone this repository into a folder named **exactly `LSP-openplanet`**:

   ```sh
   git clone https://github.com/clankercode/lsp-openplanet-sublime.git LSP-openplanet
   ```

   The package folder name is part of LSP's registration API. Do not leave it named `lsp-openplanet-sublime`. Restart Sublime after installing or updating LSP.
3. Install the server using one of these methods:

   ```sh
   npm install -g openplanet-lsp
   # Alternatively, with the Rust toolchain:
   cargo install openplanet-lsp
   ```

   Or download the appropriate archive from [server releases](https://github.com/clankercode/lsp-openplanet/releases/latest), extract it, and configure the executable path below. The **LSP-openplanet: Install Server / Help** command opens downloads, documentation, or settings. It does not silently download or execute software.
4. Open your plugin folder containing `info.toml`, then open `Main.as`. `.as` files use the included AngelScript syntax. `info.toml` retains TOML syntax and receives server diagnostics. Other TOML files do not attach to this server.

Once accepted, install **LSP-openplanet** from Package Control instead of step 2. Registry status and release instructions are in [publishing](docs/publishing.md).

## Configure

Run **Preferences: LSP-openplanet Settings**. On GUI launches PATH may differ from your terminal. Discovery checks PATH, `~/.cargo/bin`, `~/.local/bin`, Windows `%USERPROFILE%/AppData/Roaming/npm`, `/opt/homebrew/bin`, and `/usr/local/bin`. A nonempty `server_path` is authoritative: a bad path fails visibly instead of falling back to a different executable.

```json
{
    "server_path": "/absolute/path/to/openplanet-lsp",
    "initialization_options": {
        "openplanet_dir": "/absolute/path/to/OpenplanetNext"
    }
}
```

On Windows use `"C:/Tools/openplanet-lsp.exe"` or escaped backslashes. Paths with spaces work; do not add shell quotes around the value. `$home` and other Sublime variables are expanded. `env.PATH` accepts a string prefix or a list of directories, prepended to the editor environment.

The default `initialization_options` is empty, preserving the server's own discovery and configuration precedence. Pass only deliberate overrides, using server **snake_case** keys such as `openplanet_dir`, `plugins_dir`, `game_target`, `signature_mode`, `defines`, `unused`, `inactive_regions`, or `plugin_roots`. See [server configuration](https://github.com/clankercode/lsp-openplanet) for values. No example type database is installed into your live configuration.

Per-project settings belong in your `.sublime-project` file:

```json
{
    "folders": [{"path": "."}],
    "settings": {
        "LSP": {
            "LSP-openplanet": {
                "initialization_options": {"game_target": "TMNEXT"}
            }
        }
    }
}
```

The server runs as `openplanet-lsp --lsp` over stdio. Existing Sublime project folders remain the workspace roots. Without project folders, the nearest ancestor containing `info.toml` or `.openplanet-lsp.toml` becomes the root; otherwise the file's directory is used. Additional loose plugins in the same window are advertised as additional workspace folders. Opening the plugin folder explicitly is recommended for predictable workspace-wide indexing.

The bundled syntax builds on Sublime's C++ grammar with AngelScript keywords and handles. It highlights common constructs; the server supplies semantic information. Files already using a custom syntax keep that choice. If another package claims `.as`, select **AngelScript** in the syntax menu. Default ActionScript and Plain Text associations are replaced for `.as` files only.

## Troubleshooting

- **No server / startup failure:** run `openplanet-lsp --version` in a terminal. Set `server_path` if the GUI cannot find it, then run **LSP: Restart Server**. After a failed startup LSP may disable the server for that window; re-enable **LSP-openplanet** with **LSP: Enable Language Server in Project** or reopen the window.
- **No highlighting or diagnostics:** verify syntax is AngelScript for `.as` and TOML for `info.toml`, LSP is enabled, and the folder name is `LSP-openplanet`. Unsaved buffers are deliberately excluded until saved.
- **Missing game symbols:** configure your real Openplanet directory, or let the server auto-detect it. Check **LSP: Toggle Log Panel** and **LSP: Troubleshoot Server**. Never use a stub database as a production default.
- **Settings seem ignored:** restart the server after changing startup options. The server prioritizes explicit initialization options, then plugin/workspace `.openplanet-lsp.toml`, user configuration, then discovery.
- **Other TOML files:** exclusion is intentional. This package only attaches TOML support to files named exactly `info.toml`.
- **Server updates:** update via your chosen npm/Cargo/archive method; this package does not manage server versions.

## Development

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_package.py
```

CI runs the focused tests on Linux, macOS, and Windows. Unit tests use a small Sublime API boundary fake; they do not replace the [real-editor smoke test](docs/verification.md). See [API research](docs/api-research.md) for the pinned LSP contract.

## License

Choose either **Unlicense OR CC0-1.0**. Complete texts: [UNLICENSE](UNLICENSE) and [LICENSE-CC0](LICENSE-CC0). This choice covers original code, documentation, examples, and screenshots. The package references Sublime's built-in C++ grammar without bundling it. Sublime Text, LSP, and openplanet-lsp retain their own licenses.
