"""Unit tests for ANSI parsing and text rendering."""

from __future__ import annotations

import unittest

from matrix_display.led_controller import MATRIX_WIDTH
from matrix_display.rendering import (
    BLACK,
    GREEN,
    RED,
    normalize_input_text,
    parse_ansi_text,
    render_message,
)


def _lit_bounds(frame: tuple[tuple[tuple[int, int, int], ...], ...]) -> tuple[int, int]:
    lit_columns = [
        column
        for column in range(len(frame[0]))
        if any(pixel != BLACK for row in frame for pixel in [row[column]])
    ]
    return min(lit_columns), max(lit_columns)


class RenderingTests(unittest.TestCase):
    def test_normalize_input_text_strips_one_trailing_newline(self) -> None:
        self.assertEqual("hello", normalize_input_text("hello\n"))
        self.assertEqual("hello", normalize_input_text("hello\r\n"))
        self.assertEqual("a b", normalize_input_text("a\nb"))

    def test_parse_ansi_text_tracks_basic_colors(self) -> None:
        spans = parse_ansi_text("\x1b[31mRED \x1b[32mGREEN\x1b[0m WHITE")

        self.assertEqual(("RED ", RED), (spans[0].text, spans[0].color))
        self.assertEqual(("GREEN", GREEN), (spans[1].text, spans[1].color))
        self.assertEqual(" WHITE", spans[2].text)

    def test_render_message_centers_short_text(self) -> None:
        rendered = render_message("HI")

        self.assertFalse(rendered.scrolls)
        self.assertEqual(1, len(rendered.frames))

        left, right = _lit_bounds(rendered.final_frame)
        self.assertEqual((MATRIX_WIDTH - rendered.content_width) // 2, left)
        self.assertEqual(left + rendered.content_width - 1, right)

    def test_render_message_scrolls_long_text(self) -> None:
        rendered = render_message("THIS MESSAGE IS TOO WIDE FOR THE DISPLAY")

        self.assertTrue(rendered.scrolls)
        self.assertGreater(rendered.content_width, MATRIX_WIDTH)
        self.assertGreater(len(rendered.frames), 1)
        self.assertEqual(rendered.frames[-1], rendered.final_frame)

    def test_render_message_preserves_span_colors(self) -> None:
        rendered = render_message("\x1b[31mA\x1b[32mB")
        colors = {pixel for row in rendered.final_frame for pixel in row}

        self.assertIn(RED, colors)
        self.assertIn(GREEN, colors)


if __name__ == "__main__":
    unittest.main()
