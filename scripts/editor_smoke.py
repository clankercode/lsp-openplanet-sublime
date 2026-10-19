# SPDX-License-Identifier: Unlicense OR CC0-1.0
"""Copy into a disposable Sublime Packages/User directory; see docs/verification.md.
Never generates diagnostics: it observes the live LSP session and edits a buffer.
"""
import json
from pathlib import Path
import traceback

import sublime
import sublime_plugin

OUTPUT = Path('/tmp/lsp-sublime-smoke.json')
RESULT = {}
SOURCE = None
WINDOW = None
ORIGINAL = None


class OpenplanetSmokeReplaceCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        self.view.replace(edit, sublime.Region(0, self.view.size()), text)


def buffers():
    from LSP.plugin.core.registry import windows
    return [b for session in windows.lookup(WINDOW).get_sessions()
            if session.config.name == 'LSP-openplanet' for b in session.session_buffers_async()]


def record():
    return [{'uri': b.get_uri(), 'language_id': b.get_language_id(),
             'diagnostics': [d for d, region in b.diagnostics]} for b in buffers()]


def later(callback, delay=2500):
    def safe():
        try:
            callback()
        except Exception:
            RESULT['error'] = traceback.format_exc()
            OUTPUT.write_text(json.dumps(RESULT, indent=2))
            if SOURCE is not None and ORIGINAL is not None:
                SOURCE.run_command('openplanet_smoke_replace', {'text': ORIGINAL})
    sublime.set_timeout(safe, delay)


def begin():
    global SOURCE, WINDOW, ORIGINAL
    SOURCE = next(v for w in sublime.windows() for v in w.views()
                  if v.file_name() and v.file_name().endswith('/examples/diagnostics/Main.as'))
    WINDOW = SOURCE.window()
    WINDOW.focus_view(SOURCE)
    ORIGINAL = SOURCE.substr(sublime.Region(0, SOURCE.size()))
    RESULT['sublime_version'] = sublime.version()
    RESULT['before'] = record()
    assert any(d['message'] == 'undefined identifier `mesage`' for b in RESULT['before'] for d in b['diagnostics'])
    SOURCE.run_command('openplanet_smoke_replace', {'text': ORIGINAL.replace('print(mesage)', 'print(message)')})
    later(corrected)


def corrected():
    RESULT['corrected'] = record()
    assert not any('mesage' in d['message'] for b in RESULT['corrected'] for d in b['diagnostics'])
    SOURCE.run_command('openplanet_smoke_replace', {'text': ORIGINAL})
    manifest = str(Path(SOURCE.file_name()).with_name('info.toml'))
    WINDOW.open_file(manifest)
    unrelated = Path('/tmp/lsp-sublime-unrelated.toml')
    unrelated.write_text('[unrelated]\nvalue = true\n')
    WINDOW.open_file(str(unrelated))
    later(final)


def final():
    from LSP.plugin.core.registry import windows
    RESULT['final'] = record()
    assert any(b['uri'].endswith('/info.toml') and b['language_id'] == 'toml' for b in RESULT['final'])
    assert not any(b['uri'].endswith('/lsp-sublime-unrelated.toml') for b in RESULT['final'])
    assert any(d['message'] == 'undefined identifier `mesage`' for b in RESULT['final'] for d in b['diagnostics'])
    RESULT['workspace_folders'] = [f.path for s in windows.lookup(WINDOW).get_sessions() for f in s.get_workspace_folders()]
    RESULT['result'] = 'PASS'
    OUTPUT.write_text(json.dumps(RESULT, indent=2))
    WINDOW.focus_view(SOURCE)
    WINDOW.run_command('hide_panel')
    WINDOW.run_command('lsp_show_diagnostics_panel')


def plugin_loaded():
    later(begin, 4000)
