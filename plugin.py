# SPDX-License-Identifier: Unlicense OR CC0-1.0
import os
import webbrowser

import sublime
import sublime_plugin
from LSP.plugin import LspPlugin, PluginStartError, WorkspaceFolder

from .core import accepts_file, discover_server, project_root


class OpenplanetPlugin(LspPlugin):
    @classmethod
    def is_applicable_async(cls, context):
        return accepts_file(context.view.file_name()) and super().is_applicable_async(context)

    @classmethod
    def on_pre_start_async(cls, context):
        explicit = context.configuration.get("server_path", "")
        if isinstance(explicit, str):
            explicit = sublime.expand_variables(explicit, context.variables)
        path = os.environ.get("PATH", "")
        configured_path = context.configuration.env.get("PATH")
        if isinstance(configured_path, list):
            path = os.pathsep.join(sublime.expand_variables(configured_path, context.variables)) + os.pathsep + path
        elif isinstance(configured_path, str):
            path = sublime.expand_variables(configured_path, context.variables)
        try:
            context.variables["openplanet_server"] = discover_server(explicit, path=path)
        except ValueError as error:
            raise PluginStartError(str(error)) from error
        if not context.workspace_folders and context.view.file_name():
            root = project_root(context.view.file_name())
            context.workspace_folders.append(WorkspaceFolder.from_path(root))
            context.working_directory = root


class LspOpenplanetInstallServerCommand(sublime_plugin.WindowCommand):
    def run(self):
        choices = [
            ["Download a server release", "Open the official platform downloads"],
            ["Installation guide", "npm, Cargo, PATH, and troubleshooting"],
            ["Configure server path", "Set an absolute path to openplanet-lsp"],
        ]
        self.window.show_quick_panel(choices, self._select)

    def _select(self, index):
        if index == 0:
            webbrowser.open("https://github.com/clankercode/lsp-openplanet/releases/latest")
        elif index == 1:
            webbrowser.open("https://github.com/clankercode/lsp-openplanet-sublime#install")
        elif index == 2:
            self.window.run_command("edit_settings", {
                "base_file": "${packages}/LSP-openplanet/LSP-openplanet.sublime-settings"})


def associate_source(view):
    filename = view.file_name()
    syntax = view.syntax()
    if filename and filename.lower().endswith(".as") and (
        syntax is None or syntax.scope in ("source.actionscript", "text.plain")
    ):
        view.assign_syntax("Packages/LSP-openplanet/AngelScript.sublime-syntax")


class OpenplanetSyntaxListener(sublime_plugin.EventListener):
    def on_load(self, view):
        associate_source(view)


def plugin_loaded():
    for window in sublime.windows():
        for view in window.views():
            associate_source(view)
    OpenplanetPlugin.register()


def plugin_unloaded():
    OpenplanetPlugin.unregister()
