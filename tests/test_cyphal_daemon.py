"""Unit tests for the PyCyphal matrix_display daemon."""

from __future__ import annotations

import asyncio
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from matrix_display.cyphal_daemon import run_daemon


class FakeSubscriber:
    def __init__(self, messages: list[object]) -> None:
        self.pattern = "matrix_display_maksim/text"
        self._messages = list(messages)
        self.closed = False

    def __aiter__(self) -> FakeSubscriber:
        return self

    async def __anext__(self) -> SimpleNamespace:
        await asyncio.sleep(0)
        if not self._messages:
            raise StopAsyncIteration
        return SimpleNamespace(message=self._messages.pop(0))

    def close(self) -> None:
        self.closed = True


class FakeNode:
    def __init__(self, messages: list[object]) -> None:
        self.transport = "fake-transport"
        self.subscriber = FakeSubscriber(messages)
        self.subscribed_topic: str | None = None
        self.closed = False

    def subscribe(self, topic: str) -> FakeSubscriber:
        self.subscribed_topic = topic
        return self.subscriber

    def close(self) -> None:
        self.closed = True


class CyphalDaemonTests(unittest.TestCase):
    def test_run_daemon_displays_received_utf8_messages(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "matrix_display.toml"
            config_path.write_text(
                "[[display]]\n"
                'target_display = "maksim"\n'
                'controller_ip = "192.168.1.201"\n',
                encoding="utf-8",
            )
            node = FakeNode([b"Hello\n", "World"])
            factory_kwargs: dict[str, Any] = {}
            display_calls: list[tuple[str, str]] = []
            status_messages: list[str] = []

            def node_factory(**kwargs: Any) -> FakeNode:
                factory_kwargs.update(kwargs)
                return node

            def display_func(
                message: str, *, target_ip: str, controller_factory: object
            ) -> None:
                display_calls.append((message, target_ip))

            asyncio.run(
                run_daemon(
                    target="maksim",
                    config_path=config_path,
                    node_factory=node_factory,
                    display_func=display_func,
                    status=status_messages.append,
                )
            )

        self.assertEqual(
            {"home": "matrix_display_maksim", "namespace": ""}, factory_kwargs
        )
        self.assertEqual("~/text", node.subscribed_topic)
        self.assertEqual(
            [("Hello\n", "192.168.1.201"), ("World", "192.168.1.201")],
            display_calls,
        )
        self.assertTrue(node.subscriber.closed)
        self.assertTrue(node.closed)
        self.assertTrue(any("fake-transport" in message for message in status_messages))

    def test_run_daemon_ignores_invalid_utf8_and_keeps_listening(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "matrix_display.toml"
            config_path.write_text(
                "[[display]]\n"
                'target_display = "maksim"\n'
                'controller_ip = "192.168.1.201"\n',
                encoding="utf-8",
            )
            node = FakeNode([b"\xff", b"OK"])
            display_calls: list[str] = []
            status_messages: list[str] = []

            def display_func(
                message: str, *, target_ip: str, controller_factory: object
            ) -> None:
                display_calls.append(message)

            asyncio.run(
                run_daemon(
                    target="maksim",
                    config_path=config_path,
                    node_factory=lambda **_: node,
                    display_func=display_func,
                    status=status_messages.append,
                )
            )

        self.assertEqual(["OK"], display_calls)
        self.assertTrue(any("ignored message" in message for message in status_messages))


if __name__ == "__main__":
    unittest.main()
