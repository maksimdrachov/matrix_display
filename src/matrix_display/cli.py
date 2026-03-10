"""CLI for sending text directly to the matrix display controller."""

from __future__ import annotations

import argparse
import math
import sys
import time
from pathlib import Path
from typing import Callable, Mapping, TextIO

from .config import DEFAULT_CONFIG_PATH, resolve_controller_ip
from .led_controller import LedController
from .rendering import normalize_input_text, render_message

DEFAULT_HOLD_SECONDS = 0.5


def main(
    argv: list[str] | None = None,
    stdin: TextIO | None = None,
    env: Mapping[str, str] | None = None,
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
        controller_ip = resolve_controller_ip(
            args.controller_ip,
            env=env,
            config_path=args.config,
        )
        rendered = render_message(message)
        controller = controller_factory(target_ip=controller_ip)
        frame_interval = 1 / getattr(controller, "fps", 30)
        hold_frames = max(
            1, math.ceil(getattr(controller, "fps", 30) * DEFAULT_HOLD_SECONDS)
        )

        try:
            for frame in rendered.frames:
                controller.push_frame(frame)
                sleep(frame_interval)

            for _ in range(hold_frames):
                controller.push_frame(rendered.final_frame)
                sleep(frame_interval)
        finally:
            controller.close()
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
        "--controller-ip",
        help="Target PixLite controller IP address.",
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
