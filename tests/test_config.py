"""Unit tests for configuration loading."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from matrix_display.config import load_config, resolve_controller_ip
from matrix_display.led_controller import DEFAULT_TARGET_IP


class ConfigTests(unittest.TestCase):
    def test_load_config_reads_controller_ip(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matrix_display.toml"
            path.write_text('controller_ip = "192.168.1.77"\n', encoding="utf-8")

            config = load_config(path)

        self.assertEqual("192.168.1.77", config.controller_ip)

    def test_resolve_controller_ip_uses_cli_before_env_and_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matrix_display.toml"
            path.write_text('controller_ip = "192.168.1.77"\n', encoding="utf-8")

            controller_ip = resolve_controller_ip(
                "192.168.1.10",
                env={"MATRIX_DISPLAY_TARGET_IP": "192.168.1.20"},
                config_path=path,
            )

        self.assertEqual("192.168.1.10", controller_ip)

    def test_resolve_controller_ip_uses_env_before_config(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matrix_display.toml"
            path.write_text('controller_ip = "192.168.1.77"\n', encoding="utf-8")

            controller_ip = resolve_controller_ip(
                None,
                env={"MATRIX_DISPLAY_TARGET_IP": "192.168.1.20"},
                config_path=path,
            )

        self.assertEqual("192.168.1.20", controller_ip)

    def test_resolve_controller_ip_uses_config_before_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matrix_display.toml"
            path.write_text('controller_ip = "192.168.1.77"\n', encoding="utf-8")

            controller_ip = resolve_controller_ip(None, env={}, config_path=path)

        self.assertEqual("192.168.1.77", controller_ip)

    def test_resolve_controller_ip_falls_back_to_default(self) -> None:
        controller_ip = resolve_controller_ip(
            None, env={}, config_path=Path("/tmp/nope")
        )

        self.assertEqual(DEFAULT_TARGET_IP, controller_ip)

    def test_load_config_rejects_unknown_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "matrix_display.toml"
            path.write_text(
                'controller_ip = "192.168.1.77"\nuniverses = [1]\n', encoding="utf-8"
            )

            with self.assertRaisesRegex(ValueError, "unsupported config keys"):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
