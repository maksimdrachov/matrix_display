"""Unit tests for the matrix_display CLI."""

from __future__ import annotations

import io
import unittest

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
    def test_main_renders_stdin_to_target(self) -> None:
        created: list[FakeLedController] = []

        def factory(*, target_ip: str) -> FakeLedController:
            controller = FakeLedController(target_ip=target_ip)
            created.append(controller)
            return controller

        stderr = io.StringIO()

        result = main(
            ["--target", "192.168.1.201"],
            stdin=io.StringIO("Hello\n"),
            controller_factory=factory,
            sleep=lambda _: None,
            stderr=stderr,
        )

        self.assertEqual(0, result)
        self.assertEqual("", stderr.getvalue())
        self.assertEqual("192.168.1.201", created[0].target_ip)
        self.assertGreater(len(created[0].frames), 1)
        self.assertTrue(created[0].closed)

    def test_main_accepts_short_target_flag(self) -> None:
        result = main(
            ["-t", "192.168.1.201"],
            stdin=io.StringIO("Hello\n"),
            controller_factory=lambda **_: FakeLedController("192.168.1.201"),
            sleep=lambda _: None,
            stderr=io.StringIO(),
        )

        self.assertEqual(0, result)

    def test_main_rejects_empty_messages(self) -> None:
        stderr = io.StringIO()

        result = main(
            ["--target", "192.168.1.201"],
            stdin=io.StringIO("\n"),
            controller_factory=lambda **_: FakeLedController("192.168.1.201"),
            sleep=lambda _: None,
            stderr=stderr,
        )

        self.assertEqual(1, result)
        self.assertIn("expected a message on stdin", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
