"""Unit tests for the matrix_display CLI."""

from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path

from matrix_display.cli import main


class FakeLedController:
    """Minimal controller stub that captures rendered frames."""

    def __init__(self, target_ip: str) -> None:
        self.target_ip = target_ip
        self.fps = 30
        self.frames: list[tuple[tuple[tuple[int, int, int], ...], ...]] = []
        self.closed = False

    def push_frame(self, frame: tuple[tuple[tuple[int, int, int], ...], ...]) -> None:
        self.frames.append(frame)

    def close(self) -> None:
        self.closed = True


class CliTests(unittest.TestCase):
    def test_main_renders_stdin_and_uses_configured_controller_ip(self) -> None:
        created: list[FakeLedController] = []

        def factory(*, target_ip: str) -> FakeLedController:
            controller = FakeLedController(target_ip=target_ip)
            created.append(controller)
            return controller

        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "matrix_display.toml"
            config_path.write_text(
                'controller_ip = "192.168.1.201"\n', encoding="utf-8"
            )
            stderr = io.StringIO()

            result = main(
                ["--config", str(config_path)],
                stdin=io.StringIO("Hello\n"),
                env={},
                controller_factory=factory,
                sleep=lambda _: None,
                stderr=stderr,
            )

        self.assertEqual(0, result)
        self.assertEqual("", stderr.getvalue())
        self.assertEqual("192.168.1.201", created[0].target_ip)
        self.assertGreater(len(created[0].frames), 1)
        self.assertTrue(created[0].closed)

    def test_main_uses_cli_ip_before_env_and_config(self) -> None:
        created: list[FakeLedController] = []

        def factory(*, target_ip: str) -> FakeLedController:
            controller = FakeLedController(target_ip=target_ip)
            created.append(controller)
            return controller

        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "matrix_display.toml"
            config_path.write_text(
                'controller_ip = "192.168.1.201"\n', encoding="utf-8"
            )

            result = main(
                ["--config", str(config_path), "--controller-ip", "192.168.1.9"],
                stdin=io.StringIO("Hello\n"),
                env={"MATRIX_DISPLAY_TARGET_IP": "192.168.1.8"},
                controller_factory=factory,
                sleep=lambda _: None,
                stderr=io.StringIO(),
            )

        self.assertEqual(0, result)
        self.assertEqual("192.168.1.9", created[0].target_ip)

    def test_main_rejects_empty_messages(self) -> None:
        stderr = io.StringIO()
        result = main(
            [],
            stdin=io.StringIO("\n"),
            env={},
            controller_factory=lambda **_: FakeLedController("192.168.1.201"),
            sleep=lambda _: None,
            stderr=stderr,
        )

        self.assertEqual(1, result)
        self.assertIn("expected a message on stdin", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
