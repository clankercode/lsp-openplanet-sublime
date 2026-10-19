# SPDX-License-Identifier: Unlicense OR CC0-1.0
"""Editor-independent path discovery and document selection."""
import os
from pathlib import Path
import shutil


def accepts_file(filename):
    if not filename:
        return False
    path = Path(filename)
    return path.suffix.lower() == ".as" or path.name == "info.toml"


def discover_server(explicit="", path=None, home=None):
    """An explicit setting is authoritative; never hide a bad path with fallback."""
    if not isinstance(explicit, str):
        raise ValueError("server_path must be a string")
    if explicit:
        candidate = os.path.expanduser(explicit)
        result = shutil.which(candidate, path=path)
        if result:
            return result
        raise ValueError("Configured server_path is not executable: " + candidate)
    result = shutil.which("openplanet-lsp", path=path)
    if result:
        return result
    home = Path(home) if home is not None else Path.home()
    for folder in (home / ".cargo" / "bin", home / ".local" / "bin",
                   home / "AppData" / "Roaming" / "npm", Path("/opt/homebrew/bin"),
                   Path("/usr/local/bin")):
        result = shutil.which("openplanet-lsp", path=str(folder))
        if result:
            return result
    raise ValueError("openplanet-lsp was not found. Run LSP-openplanet: Install Server / Help "
                     "or set server_path in LSP-openplanet settings, then restart the server.")


def project_root(filename):
    """Nearest plugin/config root, with a useful saved-file fallback."""
    parent = Path(filename).resolve().parent
    for directory in (parent,) + tuple(parent.parents):
        if any((directory / marker).is_file() for marker in ("info.toml", ".openplanet-lsp.toml")):
            return str(directory)
    return str(parent)
