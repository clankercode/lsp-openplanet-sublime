# Publishing and installation channel

Canonical source: https://github.com/clankercode/lsp-openplanet-sublime

Package name: **LSP-openplanet**. Keep the installed package directory and archive root compatible with this name; LSP derives its session/settings name from it.

## Release checklist

1. Run `python3 -m unittest discover -s tests -v` and `python3 scripts/validate_package.py`.
2. Run the actual-editor smoke procedure in [verification](verification.md); keep its precise limits.
3. Run the official package checker with SublimeLSP's addon:

   ```sh
   git clone https://github.com/sublimelsp/lsp-package-reviewer-checks.git /tmp/lsp-package-reviewer-checks
   cd /tmp/lsp-package-reviewer-checks
   uv sync --group dev
   uv run st_package_reviewer --add-file-checkers lsp_review_checks \
     --exclude CheckSettingsMenuEntry --package-name LSP-openplanet \
     /absolute/path/to/lsp-openplanet-sublime
   ```

4. Commit, push, and tag `vMAJOR.MINOR.PATCH`; publish a GitHub release with the tested versions/limitations. Package Control follows tags and generates its own `package-metadata.json`; do not commit that generated file.
5. Docs are served by GitHub Pages from the main branch `/docs` directory. Enable that source in repository Settings → Pages, or use the REST API with branch `main`, path `/docs`.

## Package Control submission

LSP helper packages belong in **https://github.com/sublimelsp/repository**, as directed by the main Package Control registry. This is a GitHub-only process; no marketplace account is needed.

Add the following entry to `repository.json` under `packages`, sorted as `LSP-openplanet`:

```json
{
    "details": "https://github.com/clankercode/lsp-openplanet-sublime",
    "name": "LSP-openplanet",
    "labels": ["lsp", "angelscript", "openplanet"],
    "releases": [{"sublime_text": ">=4200", "tags": true}]
}
```

Fork the registry using your GitHub account, branch from its `main`, commit only this entry, and open a PR titled **Add LSP-openplanet**. Explain that it requires LSP 2.16+, discovers an installed server, and contains full licenses plus real-editor test evidence. The registry's review bots may comment automatically. The submission status/URL is recorded below after publication.

End users must install LSP separately; Package Control libraries are not a mechanism for installing the LSP editor package. `LSP-openplanet` uses no extra Python libraries beyond LSP itself and the standard library.

## Submission status

Submitted [sublimelsp/repository#189](https://github.com/sublimelsp/repository/pull/189) on 2026-10-19. It remains subject to registry maintainer review. Public source and tagged releases are available now; manual installation works before registry acceptance.

Documentation is published at https://clankercode.github.io/lsp-openplanet-sublime/ from `main:/docs`.
