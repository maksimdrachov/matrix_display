"""PyCyphal subscriber daemon for matrix display text messages."""

from __future__ import annotations

import argparse
import asyncio
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, TextIO

from .config import DEFAULT_CONFIG_PATH, resolve_controller_ip
from .display import display_text
from .led_controller import LedController

DEFAULT_TOPIC = "~/text"

DisplayFunction = Callable[..., None]
NodeFactory = Callable[..., Any]
StatusCallback = Callable[[str], None]


def main(
    argv: list[str] | None = None,
    *,
    stderr: TextIO | None = None,
    node_factory: NodeFactory | None = None,
    display_func: DisplayFunction = display_text,
) -> int:
    """Run the PyCyphal matrix_display daemon."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    error_stream = stderr or sys.stderr
    status = None if args.quiet else lambda message: print(message, file=error_stream)

    try:
        asyncio.run(
            run_daemon(
                target=args.target,
                config_path=args.config,
                home=args.home,
                namespace=args.namespace,
                topic=args.topic,
                node_factory=node_factory,
                display_func=display_func,
                status=status,
            )
        )
    except KeyboardInterrupt:
        return 130
    except (RuntimeError, ValueError) as error:
        error_stream.write(f"matrix_display_cyphal: {error}\n")
        return 1

    return 0


async def run_daemon(
    *,
    target: str,
    config_path: Path | None = None,
    home: str | None = None,
    namespace: str = "",
    topic: str = DEFAULT_TOPIC,
    controller_factory: Callable[..., LedController] = LedController,
    node_factory: NodeFactory | None = None,
    display_func: DisplayFunction = display_text,
    status: StatusCallback | None = None,
) -> None:
    """Subscribe to a PyCyphal text topic and display each received message."""
    controller_ip = resolve_controller_ip(target, config_path=config_path)
    home_name = home or f"matrix_display_{target}"
    node = (
        node_factory(home=home_name, namespace=namespace)
        if node_factory is not None
        else _make_default_node(home=home_name, namespace=namespace)
    )
    subscriber = None

    try:
        subscriber = node.subscribe(topic)
        if status is not None:
            status(f"matrix_display_cyphal: transport {node.transport}")
            status(
                "matrix_display_cyphal: "
                f"subscribed to {subscriber.pattern} for target {target} ({controller_ip})"
            )

        async for arrival in subscriber:
            try:
                message = _decode_text_message(arrival.message)
                await asyncio.to_thread(
                    display_func,
                    message,
                    target_ip=controller_ip,
                    controller_factory=controller_factory,
                )
            except Exception as error:
                if status is not None:
                    status(f"matrix_display_cyphal: ignored message: {error}")
    finally:
        if subscriber is not None:
            subscriber.close()
        node.close()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="matrix_display_cyphal",
        description="Subscribe to a PyCyphal text topic and display received text.",
    )
    parser.add_argument(
        "-t",
        "--target",
        required=True,
        help="Named target display from ~/.matrix_display.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"Path to the TOML config file (default: {DEFAULT_CONFIG_PATH}).",
    )
    parser.add_argument(
        "--home",
        help="PyCyphal node home name (default: matrix_display_<target>).",
    )
    parser.add_argument(
        "--namespace",
        default="",
        help="PyCyphal namespace passed to Node.new() (default: empty).",
    )
    parser.add_argument(
        "--topic",
        default=DEFAULT_TOPIC,
        help=f"PyCyphal topic to subscribe to (default: {DEFAULT_TOPIC}).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress daemon startup and per-message error output.",
    )
    return parser


def _make_default_node(*, home: str, namespace: str) -> Any:
    try:
        from pycyphal2 import Node
        from pycyphal2.udp import UDPTransport
    except ModuleNotFoundError as error:
        raise RuntimeError(
            "PyCyphal UDP support is not installed; install with "
            "`python3 -m pip install -e '.[cyphal]'`"
        ) from error

    return Node.new(UDPTransport.new(), home=home, namespace=namespace)


def _decode_text_message(message: object) -> str:
    if isinstance(message, str):
        return message
    if isinstance(message, bytes):
        return message.decode("utf-8")
    if isinstance(message, bytearray):
        return bytes(message).decode("utf-8")
    if isinstance(message, memoryview):
        return message.tobytes().decode("utf-8")
    raise ValueError("expected a UTF-8 text message")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
