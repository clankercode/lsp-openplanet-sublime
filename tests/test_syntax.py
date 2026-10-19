import unittest
from pathlib import Path


class SyntaxTests(unittest.TestCase):
    def test_includes_cpp_without_incompatible_inheritance(self):
        source = (Path(__file__).resolve().parents[1] / 'AngelScript.sublime-syntax').read_text()
        self.assertNotIn('extends:', source)
        self.assertIn('include: scope:source.c++', source)
        self.assertIn('scope: source.angelscript', source)
