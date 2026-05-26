"""CLI for sending text directly to the matrix display controller."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Callable, TextIO

from .config import DEFAULT_CONFIG_PATH, resolve_controller_ip
from .display import display_text
from .led_controller import LedController
from .rendering import normalize_input_text


def main(
    argv: list[str] | None = None,
    stdin: TextIO | None = None,
    controller_factory: Callable[..., LedController] = LedController,
    sleep: Callable[[float], None] = time.sleep,
    stderr: TextIO | None = None,
) -> int:
    """Run the matrix_display CLI."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    error_stream = stderr or sys.stderr

    try:
        message = _read_message(stdin or sys.stdin)
        controller_ip = resolve_controller_ip(args.target, config_path=args.config)
        display_text(
            message,
            target_ip=controller_ip,
            controller_factory=controller_factory,
            sleep=sleep,
        )
    except ValueError as error:
        error_stream.write(f"matrix_display: {error}\n")
        return 1

    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="matrix_display",
        description="Render text from stdin directly to the matrix display.",
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
    return parser


def _read_message(stream: TextIO) -> str:
    message = normalize_input_text(stream.read())
    if not message:
        raise ValueError("expected a message on stdin")
    return message
