import unittest
from unittest.mock import Mock, patch
import tempfile
from pathlib import Path

import requests

from core import updater_service


class UpdaterServiceTests(unittest.TestCase):
    @patch("core.updater_service.requests.get")
    def test_release_check_uses_github_https_without_dns_socket_probe(self, get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"tag_name": "v9.9.9", "assets": []}
        get.return_value = response

        data, error = updater_service.get_latest_release_details()

        self.assertIsNone(error)
        self.assertEqual("v9.9.9", data["tag_name"])
        get.assert_called_once_with(
            updater_service.GITHUB_API_URL,
            headers=updater_service.GITHUB_HEADERS,
            timeout=(5, 15),
        )

    @patch("core.updater_service.requests.get")
    def test_tls_error_is_not_reported_as_no_internet(self, get):
        get.side_effect = requests.exceptions.SSLError("certificate verify failed")

        data, error = updater_service.get_latest_release_details()

        self.assertIsNone(data)
        self.assertEqual("tls-error", error["state"])
        self.assertIn("Sertifika", error["message"])

    @patch("core.updater_service.requests.get")
    def test_connection_error_mentions_dns_or_firewall(self, get):
        get.side_effect = requests.exceptions.ConnectionError("blocked")

        data, error = updater_service.get_latest_release_details()

        self.assertIsNone(data)
        self.assertEqual("connection-failed", error["state"])
        self.assertIn("güvenlik duvarı", error["message"])

    @patch("core.updater_service.requests.get")
    def test_download_reports_progress_without_content_length(self, get):
        response = Mock()
        response.headers = {}
        response.raise_for_status.return_value = None
        response.iter_content.return_value = [b"abc", b"defg"]
        get.return_value = response
        progress = []

        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "update.exe"
            ok = updater_service.download_update_file(
                "https://example.test/update.exe",
                str(destination),
                lambda downloaded, total: progress.append((downloaded, total)),
            )
            self.assertEqual(b"abcdefg", destination.read_bytes())

        self.assertTrue(ok)
        self.assertEqual([(3, 0), (7, 0)], progress)


if __name__ == "__main__":
    unittest.main()
