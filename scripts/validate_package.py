#!/usr/bin/env python3
# SPDX-License-Identifier: Unlicense OR CC0-1.0
"""Validate shipped configuration and syntax prerequisites without Sublime."""
import ast
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for path in root.rglob("*.py"):
    ast.parse(path.read_text(), feature_version=(3, 8))
for name in ("LSP-openplanet.sublime-settings", "LSP-openplanet.sublime-commands", "Main.sublime-menu", "messages.json", "package-metadata.json"):
    json.loads((root / name).read_text())
settings = json.loads((root / "LSP-openplanet.sublime-settings").read_text())
assert settings["command"] == ["$openplanet_server", "--lsp"]
assert settings["initialization_options"] == {}
assert settings["schemes"] == ["file"]
assert settings["selector"] == "source.angelscript | source.toml"
assert (root / "UNLICENSE").stat().st_size > 1000
assert (root / "LICENSE-CC0").stat().st_size > 6000
print("Package configuration and Python 3.8 syntax: PASS")
