# Verification

Verified on Linux x86_64 on 2026-10-19. This is evidence for the surfaces listed here, not a claim that every server feature or supported OS was exercised.

## Versions and checks

- Sublime Text **4215**, official portable Linux archive, isolated under `/tmp/lsp-sublime-research/sublime_text`.
- LSP **2.16.0**, released tag `4070-2.16.0`, commit `b51e5d8aadec452ff61275d4d6e34f697302201c`.
- openplanet-lsp **0.8.0**, existing installed release `/home/xertrov/.local/bin/openplanet-lsp --lsp`. No full server builds were run.
- Python 3.14 local unit tests: **18 tests passed**. Package validator also parses all Python as Python 3.8 syntax and checks shipped JSON, command, selectors, empty init options, and complete license texts.
- Official `st_package_reviewer` **1.4.0** from commit `406c008ab8551a3eda62c5388bdd0ab1dba5e9f9`, with the SublimeLSP menu checker: **no failures, no warnings**. [Receipt](evidence/package-review.txt).
- [Unit-test receipt](evidence/unit-tests.txt). All six CI jobs passed on Linux, macOS, and Windows using Python 3.8 and 3.13: [run 39217109786](https://github.com/clankercode/lsp-openplanet-sublime/actions/runs/39217109786), commit `9b659f951a605b1bfb3c769bbce8048a8de3d0d7`. [Machine-readable CI receipt](evidence/github-ci.json). The CI workflow tests package logic and metadata, not native GUI interaction.

## Real editor

The screenshot was captured with ImageMagick `import -window root` from our own 1440×1000 Xvfb display. It is the actual Sublime editor, including its real diagnostics panel and inline annotation, with no HTML recreation, painted diagnostics, or compositing. The sample is an original minimal plugin in this repository, dedicated under both public-domain licenses; `mesage` is deliberately misspelled.

A temporary harness reads LSP's actual session/buffer diagnostics. [`scripts/editor_smoke.py`](../scripts/editor_smoke.py) exercises the diagnostic lifecycle inside Sublime:

1. Observe the server's `undefined identifier \`mesage\`` diagnostic.
2. Correct the in-memory buffer to `message`; verify the diagnostic clears.
3. Restore the original buffer; verify the diagnostic returns.
4. Open `info.toml`; verify it is attached with TOML language ID.
5. Open unrelated TOML; verify it is excluded.

[Machine-readable editor receipt](evidence/editor-smoke.json). The harness uses explicit exceptions rather than Python `assert`: Sublime's optimized Python host disables assertions. It restores the example in memory and never saves its edits to disk.

## Reproduce

1. Download the official portable Sublime build into an empty `/tmp` directory and create its `Data` directory.
2. Install LSP 2.16+ and its declared libraries into that portable profile. This run cloned the release and extracted the libraries from `https://packages.sublimetext.com/channel_v4.json` into `Data/Lib/python314`: mdpopups 5.1.2, bracex 3.1, wcmatch 11.1, typing-extensions 4.16.0, orjson 3.13.0, and pygments 2.21.0. Package Control was downloaded but disabled in the temporary profile; this was a manual harness install, not a verified Package Control end-user install.
3. Clone/copy this repository to `Data/Packages/LSP-openplanet`; verify the folder name. Ensure `openplanet-lsp` is executable on PATH or set `server_path` in User settings.
4. Start an unused Xvfb display and a window manager on that display. Use `GDK_BACKEND=x11` and a private `XDG_RUNTIME_DIR`; a private `dbus-run-session` avoided desktop-session interference in this environment. Open `examples/diagnostics` and its `Main.as` in that portable editor.
5. Focus `Main.as`, wait for real diagnostics, then copy `scripts/editor_smoke.py` into `Data/Packages/User/`. Read `/tmp/lsp-sublime-smoke.json`; a real passing receipt contains nonempty initial and final diagnostics, empty corrected diagnostics, and an attached TOML manifest.
6. Maximize the editor, run **LSP: Show Diagnostics Panel**, capture with `DISPLAY=:<your-display> import -window root screenshot.png`. Remove temporary harnesses and terminate only the processes/displays you started.

## Limits

- Real-editor verification is Linux x86_64, Sublime 4215, LSP 2.16.0, server 0.8.0 only. macOS/Windows native editor startup and ARM were not run locally.
- Completion, hover, navigation, rename, and semantic tokens are exposed through LSP but were not separately asserted in the GUI smoke test. Diagnostics and file selection were exercised directly.
- Root discovery and multiple loose plugin roots have focused unit coverage; the GUI receipt uses one explicit plugin folder.
- Package Control registry inclusion depends on maintainer review; submitting a PR does not make the package available in the default channel immediately.
- No server downloader is bundled. The help command opens official installation guidance/releases; executable discovery and explicit configuration are implemented and tested.

## Review corrections

The clean-start smoke also confirms the source is sent with `language_id: angelscript`. A symlinked temporary-directory run (`TMPDIR=/proc/self/root/tmp`) passed all 18 tests after resolving expected test paths, covering the macOS `/var` alias behavior.

Real editor testing found mixed-version syntax inheritance; a red/green regression test was added and the grammar now includes the built-in C++ scope. Independent API review found and fixed `ClientConfig` access, PATH normalization, crossed syntax/file selection, and advertising additional loose roots. The local registry checker led to moving shared code into `lib/`, removing generated Package Control metadata from source, and aligning the settings menu.
