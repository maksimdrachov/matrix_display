"""Shared text-to-display transmission helpers."""

from __future__ import annotations

import math
import time
from collections.abc import Callable

from .led_controller import LedController
from .rendering import normalize_input_text, render_message

DEFAULT_HOLD_SECONDS = 0.5


def display_text(
    message: str,
    *,
    target_ip: str,
    controller_factory: Callable[..., LedController] = LedController,
    sleep: Callable[[float], None] = time.sleep,
    hold_seconds: float = DEFAULT_HOLD_SECONDS,
) -> None:
    """Render one message and send it to the matrix display controller."""
    normalized_message = normalize_input_text(message)
    if not normalized_message:
        raise ValueError("expected a message")

    rendered = render_message(normalized_message)
    controller = controller_factory(target_ip=target_ip)
    frame_interval = 1 / getattr(controller, "fps", 30)
    hold_frames = max(1, math.ceil(getattr(controller, "fps", 30) * hold_seconds))

    try:
        for frame in rendered.frames:
            controller.push_frame(frame)
            sleep(frame_interval)

        for _ in range(hold_frames):
            controller.push_frame(rendered.final_frame)
            sleep(frame_interval)
    finally:
        controller.close()
