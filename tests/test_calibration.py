"""Hardware calibration test for the PixLite-driven matrix."""

from __future__ import annotations

import os
import time
import unittest

from matrix_display import LedController, make_calibration_frame
from matrix_display.led_controller import DEFAULT_UNIVERSES


def _parse_universes(value: str | None) -> tuple[int, ...]:
    if not value:
        return DEFAULT_UNIVERSES
    return tuple(int(part.strip()) for part in value.split(",") if part.strip())


RUN_HARDWARE_TESTS = os.environ.get("MATRIX_DISPLAY_RUN_HARDWARE_TESTS") == "1"
TARGET_IP = os.environ.get("MATRIX_DISPLAY_TARGET_IP", "192.168.1.201")
UNIVERSES = _parse_universes(os.environ.get("MATRIX_DISPLAY_UNIVERSES"))
REFRESH_SECONDS = float(os.environ.get("MATRIX_DISPLAY_REFRESH_SECONDS", "3"))
FRAME_INTERVAL_SECONDS = float(
    os.environ.get("MATRIX_DISPLAY_FRAME_INTERVAL_SECONDS", str(1 / 30))
)


@unittest.skipUnless(
    RUN_HARDWARE_TESTS,
    "set MATRIX_DISPLAY_RUN_HARDWARE_TESTS=1 to transmit the calibration frame",
)
class CalibrationHardwareTests(unittest.TestCase):
    def test_display_calibration_frame(self) -> None:
        controller = LedController(target_ip=TARGET_IP, universes=UNIVERSES)
        frame = make_calibration_frame()
        deadline = time.monotonic() + REFRESH_SECONDS

        try:
            while time.monotonic() < deadline:
                controller.push_frame(frame)
                time.sleep(FRAME_INTERVAL_SECONDS)
        finally:
            controller.close()


if __name__ == "__main__":
    unittest.main()
