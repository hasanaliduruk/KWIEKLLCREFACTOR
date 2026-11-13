import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.versioning import read_version, render_version_resource


ROOT = Path(__file__).resolve().parents[1]


class VersioningTests(unittest.TestCase):
    def test_single_version_renders_windows_resource(self):
        release = read_version()
        template = (ROOT / "version.txt").read_text(encoding="utf-8")
        rendered = render_version_resource(template, release)
        major, minor, patch_version = map(int, release.split("."))
        self.assertIn(f"filevers=({major}, {minor}, {patch_version}, 0)", rendered)
        self.assertIn(f"prodvers=({major}, {minor}, {patch_version}, 0)", rendered)
        self.assertIn(f"StringStruct(u'FileVersion', u'{release}')", rendered)
        self.assertIn(f"StringStruct(u'ProductVersion', u'{release}')", rendered)
        self.assertNotIn("{{VERSION", rendered)

    def test_frozen_app_reads_bundled_version(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "VERSION").write_text("2.4.6\n", encoding="utf-8")
            with patch("sys.frozen", True, create=True), patch("sys._MEIPASS", folder, create=True):
                self.assertEqual("2.4.6", read_version())

    def test_invalid_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "VERSION"
            path.write_text("v1.3.18\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "major.minor.patch"):
                read_version(path)
