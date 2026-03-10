"""Unit tests for configuration loading."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from matrix_display.config import load_config, resolve_controller_ip


class ConfigTests(unittest.TestCase):
    def test_load_config_reads_named_displays(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matrix_display.toml"
            path.write_text(
                "[[display]]\n"
                'target_display = "maksim"\n'
                'controller_ip = "192.168.1.77"\n'
                "\n"
                "[[display]]\n"
                'target_display = "office"\n'
                'controller_ip = "192.168.1.88"\n',
                encoding="utf-8",
            )

            config = load_config(path)

        self.assertEqual(2, len(config.displays))
        self.assertEqual("maksim", config.displays[0].target_display)
        self.assertEqual("192.168.1.77", config.displays[0].controller_ip)

    def test_resolve_controller_ip_uses_named_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matrix_display.toml"
            path.write_text(
                "[[display]]\n"
                'target_display = "maksim"\n'
                'controller_ip = "192.168.1.77"\n',
                encoding="utf-8",
            )

            controller_ip = resolve_controller_ip("maksim", config_path=path)

        self.assertEqual("192.168.1.77", controller_ip)

    def test_resolve_controller_ip_rejects_unknown_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matrix_display.toml"
            path.write_text(
                "[[display]]\n"
                'target_display = "maksim"\n'
                'controller_ip = "192.168.1.77"\n',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "target display 'office'"):
                resolve_controller_ip("office", config_path=path)

    def test_load_config_rejects_duplicate_targets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matrix_display.toml"
            path.write_text(
                "[[display]]\n"
                'target_display = "maksim"\n'
                'controller_ip = "192.168.1.77"\n'
                "\n"
                "[[display]]\n"
                'target_display = "maksim"\n'
                'controller_ip = "192.168.1.88"\n',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "duplicate target_display"):
                load_config(path)

    def test_load_config_rejects_unknown_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matrix_display.toml"
            path.write_text(
                "[[display]]\n"
                'target_display = "maksim"\n'
                'controller_ip = "192.168.1.77"\n'
                "universes = [1]\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "unsupported display keys"):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
