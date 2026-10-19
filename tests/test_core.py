# SPDX-License-Identifier: Unlicense OR CC0-1.0
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from lib.core import accepts_file, discover_server, project_root


class SelectionTests(unittest.TestCase):
    def test_files(self):
        for name in ("Main.as", "nested/file.as", "Main.AS", "info.toml", "plugin/info.toml"):
            with self.subTest(name=name):
                self.assertTrue(accepts_file(name))
        for name in (None, "", "config.toml", "info.toml.bak", "Main.as.txt", "README", "Info.toml"):
            with self.subTest(name=name):
                self.assertFalse(accepts_file(name))


class DiscoveryTests(unittest.TestCase):
    def test_explicit_is_authoritative(self):
        with patch("lib.core.shutil.which", return_value=None) as which:
            with self.assertRaisesRegex(ValueError, "Configured server_path"):
                discover_server("/bad/path", path="/good")
            which.assert_called_once_with("/bad/path", path="/good")

    def test_explicit_and_path(self):
        for explicit in ("/opt/bin/openplanet-lsp", "openplanet-lsp", "C:/bin/openplanet-lsp.exe"):
            with self.subTest(explicit=explicit):
                with patch("lib.core.shutil.which", return_value=explicit):
                    self.assertEqual(discover_server(explicit), explicit)
        with patch("lib.core.shutil.which", return_value="/path/bin/openplanet-lsp"):
            self.assertEqual(discover_server(), "/path/bin/openplanet-lsp")

    def test_default_locations(self):
        for folder in (".cargo/bin", ".local/bin", "AppData/Roaming/npm"):
            with self.subTest(folder=folder):
                location = str(Path("/home/test") / folder)
                with patch("lib.core.shutil.which", side_effect=lambda command, path=None:
                           location + "/openplanet-lsp" if path == location else None):
                    self.assertEqual(discover_server(path="", home="/home/test"), location + "/openplanet-lsp")

    def test_missing_and_invalid(self):
        with patch("lib.core.shutil.which", return_value=None):
            with self.assertRaisesRegex(ValueError, "Install Server / Help"):
                discover_server(home="/missing")
        for bad in ([], None, 123):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "must be a string"):
                discover_server(bad)

    def test_real_executable_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix="openplanet space ") as tmp:
            executable = Path(tmp) / ("openplanet-lsp.exe" if os.name == "nt" else "openplanet-lsp")
            executable.write_text("#!/bin/sh\nexit 0\n")
            executable.chmod(0o755)
            self.assertEqual(os.path.normcase(discover_server(str(executable))), os.path.normcase(str(executable)))
            self.assertEqual(os.path.normcase(discover_server(path=tmp)), os.path.normcase(str(executable)))


class RootTests(unittest.TestCase):
    def test_nearest_marker_and_fallback(self):
        for marker in ("info.toml", ".openplanet-lsp.toml"):
            with self.subTest(marker=marker), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp).resolve()
                source = root / "plugin" / "src"
                source.mkdir(parents=True)
                self.assertEqual(project_root(str(source / "Main.as")), str(source))
                (root / marker).touch()
                self.assertEqual(project_root(str(source / "Main.as")), str(root))
                (source.parent / "info.toml").touch()
                self.assertEqual(project_root(str(source / "Main.as")), str(source.parent))
