# SPDX-License-Identifier: Unlicense OR CC0-1.0
"""Boundary tests use small API fakes; real-editor coverage is documented separately."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

from lib import core


class Base:
    @classmethod
    def is_applicable_async(cls, context):
        return context.scope_matches


class StartError(Exception):
    pass


sublime = types.ModuleType("sublime")
sublime.expand_variables = lambda value, variables: [sublime.expand_variables(x, variables) for x in value] if isinstance(value, list) else value.replace("$home", variables.get("home", ""))
sublime_plugin = types.ModuleType("sublime_plugin")
sublime_plugin.WindowCommand = object
sublime_plugin.EventListener = object
sublime.windows = lambda: []
lsp = types.ModuleType("LSP.plugin")
lsp.uri_to_filename = lambda uri: uri[7:]
lsp.LspPlugin = Base
lsp.PluginStartError = StartError
lsp.WorkspaceFolder = types.SimpleNamespace(from_path=lambda path: types.SimpleNamespace(path=path))
package = types.ModuleType("fixture_package")
package.__path__ = []
with patch.dict(sys.modules, {"sublime": sublime, "sublime_plugin": sublime_plugin, "LSP": types.ModuleType("LSP"),
                              "LSP.plugin": lsp, "fixture_package": package, "fixture_package.lib": types.ModuleType("fixture_package.lib"), "fixture_package.lib.core": core}):
    spec = importlib.util.spec_from_file_location("fixture_package.plugin", Path(__file__).resolve().parents[1] / "plugin.py")
    plugin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plugin)


class Config:
    def __init__(self, **kwargs):
        self.root_settings = kwargs
        self.env = {}
        self.initialization_options = {}


def context(filename, folders=None, **settings):
    return types.SimpleNamespace(configuration=Config(**settings), variables={"home": "/test"},
        view=types.SimpleNamespace(file_name=lambda: filename, syntax=lambda: types.SimpleNamespace(scope="source.toml" if filename and filename.endswith(".toml") else "source.angelscript")), scope_matches=True,
        workspace_folders=[] if folders is None else folders, working_directory=None)


class PluginTests(unittest.TestCase):
    def test_selector_excludes_other_toml_even_with_toml_scope(self):
        for filename, expected in (("Main.as", True), ("info.toml", True), ("other.toml", False), (None, False)):
            with self.subTest(filename=filename):
                self.assertEqual(plugin.OpenplanetPlugin.is_applicable_async(context(filename)), expected)
        ctx = context("Main.as")
        ctx.scope_matches = False
        self.assertFalse(plugin.OpenplanetPlugin.is_applicable_async(ctx))

    def test_start_sets_executable_keeps_init_options_and_workspace(self):
        folders = [object(), object()]
        ctx = context("/plugin/Main.as", folders, server_path="$home/my server")
        ctx.configuration.initialization_options = {"game_target": "turbo"}
        with patch.object(plugin, "discover_server", return_value="/resolved/server") as resolve:
            plugin.OpenplanetPlugin.on_pre_start_async(ctx)
        resolve.assert_called_once_with("/test/my server", path=plugin.os.environ.get("PATH", ""))
        self.assertEqual(ctx.variables["openplanet_server"], "/resolved/server")
        self.assertIs(ctx.workspace_folders, folders)
        self.assertEqual(len(folders), 2)
        self.assertEqual(ctx.configuration.initialization_options, {"game_target": "turbo"})

    def test_loose_file_gets_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = context(str(Path(tmp) / "Main.as"))
            with patch.object(plugin, "discover_server", return_value="/server"):
                plugin.OpenplanetPlugin.on_pre_start_async(ctx)
            self.assertEqual(ctx.workspace_folders[0].path, tmp)
            self.assertEqual(ctx.working_directory, tmp)
            self.assertEqual(ctx.configuration.initialization_options, {})

    def test_filename_syntax_pairing(self):
        for filename in ("Main.as", "info.toml", "unrelated.toml"):
            for scope in ("source.angelscript", "source.toml", "source.actionscript"):
                with self.subTest(filename=filename, scope=scope):
                    ctx = context(filename)
                    ctx.view.syntax = lambda: types.SimpleNamespace(scope=scope)
                    expected = (filename == "Main.as" and scope == "source.angelscript") or (filename == "info.toml" and scope == "source.toml")
                    self.assertEqual(plugin.OpenplanetPlugin.is_applicable_async(ctx), expected)

    def test_additional_loose_root_is_advertised_once(self):
        instance = plugin.OpenplanetPlugin()
        session = Mock()
        session.window.folders.return_value = []
        session.get_workspace_folders.return_value = [types.SimpleNamespace(path="/first")]
        instance.weaksession = lambda: session
        with patch.object(plugin, "uri_to_filename", return_value="/second/Main.as"), patch.object(plugin, "project_root", return_value="/second"):
            instance.on_pre_send_notification_async({"method":"textDocument/didOpen", "params":{"textDocument":{"uri":"file:///second/Main.as"}}})
        self.assertEqual(session.update_folders.call_args.args[0][-1].path, "/second")
        session.update_folders.reset_mock()
        with patch.object(plugin, "uri_to_filename", return_value="/first/Main.as"), patch.object(plugin, "project_root", return_value="/first"):
            instance.on_pre_send_notification_async({"method":"textDocument/didOpen", "params":{"textDocument":{"uri":"file:///first/Main.as"}}})
        session.update_folders.assert_not_called()

    def test_bad_path_becomes_visible_start_error(self):
        with patch.object(plugin, "discover_server", side_effect=ValueError("bad explicit path")):
            with self.assertRaisesRegex(StartError, "bad explicit path"):
                plugin.OpenplanetPlugin.on_pre_start_async(context("Main.as"))

    def test_environment_path_overrides(self):
        for override in ("$home/bin", ["$home/bin", "/extra"]):
            ctx = context("Main.as", [object()])
            ctx.configuration.env = {"PATH": override}
            with patch.object(plugin, "discover_server", return_value="/server") as resolve:
                plugin.OpenplanetPlugin.on_pre_start_async(ctx)
            expected = plugin.os.pathsep.join((["/test/bin"] if isinstance(override, str) else ["/test/bin", "/extra"]) + [plugin.os.environ.get("PATH", "")])
            self.assertIsInstance(ctx.configuration.env["PATH"], str)
            self.assertEqual(resolve.call_args.kwargs["path"], expected)

    def test_as_association_and_user_override(self):
        for filename, scope, expected in (("Main.as", "source.actionscript", True),
                ("Main.AS", "text.plain", True), ("Main.as", "source.angelscript", False),
                ("Main.as", "source.user-custom", False), ("info.toml", "source.toml", False)):
            with self.subTest(filename=filename, scope=scope):
                view = Mock()
                view.file_name.return_value = filename
                view.syntax.return_value = types.SimpleNamespace(scope=scope)
                plugin.associate_source(view)
                self.assertEqual(view.assign_syntax.called, expected)

    def test_registration_and_teardown(self):
        with patch.object(Base, "register", create=True) as register, patch.object(Base, "unregister", create=True) as unregister:
            plugin.plugin_loaded()
            plugin.plugin_unloaded()
            register.assert_called_once()
            unregister.assert_called_once()

    def test_install_actions_and_cancel(self):
        command = plugin.LspOpenplanetInstallServerCommand()
        command.window = Mock()
        command.run()
        self.assertEqual(len(command.window.show_quick_panel.call_args.args[0]), 3)
        with patch.object(plugin.webbrowser, "open") as browse:
            command._select(-1)
            browse.assert_not_called()
            command._select(0)
            self.assertTrue(browse.call_args.args[0].endswith("/releases/latest"))
            command._select(1)
            self.assertTrue(browse.call_args.args[0].endswith("#install"))
        command._select(2)
        self.assertEqual(command.window.run_command.call_args.args[0], "edit_settings")
