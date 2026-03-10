"""ANSI-aware text rendering for the matrix display."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from .led_controller import MATRIX_HEIGHT, MATRIX_WIDTH

Color = tuple[int, int, int]
RenderedFrame = tuple[tuple[Color, ...], ...]

BLACK: Color = (0, 0, 0)
WHITE: Color = (255, 255, 255)
RED: Color = (255, 0, 0)
GREEN: Color = (0, 255, 0)
BLUE: Color = (0, 0, 255)
YELLOW: Color = (255, 255, 0)
MAGENTA: Color = (255, 0, 255)
CYAN: Color = (0, 255, 255)

DEFAULT_COLOR = WHITE
ANSI_PATTERN = re.compile(r"\x1b\[([0-9;]*)m")
FONT_HEIGHT = 7
LETTER_SPACING = 1
VERTICAL_OFFSET = (MATRIX_HEIGHT - FONT_HEIGHT) // 2

ANSI_COLORS: dict[int, Color] = {
    30: (0, 0, 0),
    31: RED,
    32: GREEN,
    33: YELLOW,
    34: BLUE,
    35: MAGENTA,
    36: CYAN,
    37: WHITE,
    90: (128, 128, 128),
    91: (255, 85, 85),
    92: (85, 255, 85),
    93: (255, 255, 85),
    94: (85, 85, 255),
    95: (255, 85, 255),
    96: (85, 255, 255),
    97: WHITE,
}

GLYPHS: dict[str, tuple[str, ...]] = {
    " ": (
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
    ),
    "!": (
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
        "00000",
        "00100",
    ),
    '"': (
        "01010",
        "01010",
        "01010",
        "00000",
        "00000",
        "00000",
        "00000",
    ),
    "'": (
        "00100",
        "00100",
        "00100",
        "00000",
        "00000",
        "00000",
        "00000",
    ),
    "(": (
        "00010",
        "00100",
        "01000",
        "01000",
        "01000",
        "00100",
        "00010",
    ),
    ")": (
        "01000",
        "00100",
        "00010",
        "00010",
        "00010",
        "00100",
        "01000",
    ),
    "+": (
        "00000",
        "00100",
        "00100",
        "11111",
        "00100",
        "00100",
        "00000",
    ),
    ",": (
        "00000",
        "00000",
        "00000",
        "00000",
        "00110",
        "00100",
        "01000",
    ),
    "-": (
        "00000",
        "00000",
        "00000",
        "11111",
        "00000",
        "00000",
        "00000",
    ),
    ".": (
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
        "00110",
        "00110",
    ),
    "/": (
        "00001",
        "00010",
        "00100",
        "01000",
        "10000",
        "00000",
        "00000",
    ),
    ":": (
        "00000",
        "00110",
        "00110",
        "00000",
        "00110",
        "00110",
        "00000",
    ),
    ";": (
        "00000",
        "00110",
        "00110",
        "00000",
        "00110",
        "00100",
        "01000",
    ),
    "=": (
        "00000",
        "11111",
        "00000",
        "11111",
        "00000",
        "00000",
        "00000",
    ),
    "?": (
        "01110",
        "10001",
        "00001",
        "00010",
        "00100",
        "00000",
        "00100",
    ),
    "_": (
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
        "00000",
        "11111",
    ),
    "0": (
        "01110",
        "10001",
        "10011",
        "10101",
        "11001",
        "10001",
        "01110",
    ),
    "1": (
        "00100",
        "01100",
        "00100",
        "00100",
        "00100",
        "00100",
        "01110",
    ),
    "2": (
        "01110",
        "10001",
        "00001",
        "00010",
        "00100",
        "01000",
        "11111",
    ),
    "3": (
        "11110",
        "00001",
        "00001",
        "01110",
        "00001",
        "00001",
        "11110",
    ),
    "4": (
        "00010",
        "00110",
        "01010",
        "10010",
        "11111",
        "00010",
        "00010",
    ),
    "5": (
        "11111",
        "10000",
        "11110",
        "00001",
        "00001",
        "10001",
        "01110",
    ),
    "6": (
        "00110",
        "01000",
        "10000",
        "11110",
        "10001",
        "10001",
        "01110",
    ),
    "7": (
        "11111",
        "00001",
        "00010",
        "00100",
        "01000",
        "01000",
        "01000",
    ),
    "8": (
        "01110",
        "10001",
        "10001",
        "01110",
        "10001",
        "10001",
        "01110",
    ),
    "9": (
        "01110",
        "10001",
        "10001",
        "01111",
        "00001",
        "00010",
        "11100",
    ),
    "A": (
        "01110",
        "10001",
        "10001",
        "11111",
        "10001",
        "10001",
        "10001",
    ),
    "B": (
        "11110",
        "10001",
        "10001",
        "11110",
        "10001",
        "10001",
        "11110",
    ),
    "C": (
        "01110",
        "10001",
        "10000",
        "10000",
        "10000",
        "10001",
        "01110",
    ),
    "D": (
        "11110",
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "11110",
    ),
    "E": (
        "11111",
        "10000",
        "10000",
        "11110",
        "10000",
        "10000",
        "11111",
    ),
    "F": (
        "11111",
        "10000",
        "10000",
        "11110",
        "10000",
        "10000",
        "10000",
    ),
    "G": (
        "01110",
        "10001",
        "10000",
        "10111",
        "10001",
        "10001",
        "01110",
    ),
    "H": (
        "10001",
        "10001",
        "10001",
        "11111",
        "10001",
        "10001",
        "10001",
    ),
    "I": (
        "11111",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
        "11111",
    ),
    "J": (
        "00111",
        "00010",
        "00010",
        "00010",
        "00010",
        "10010",
        "01100",
    ),
    "K": (
        "10001",
        "10010",
        "10100",
        "11000",
        "10100",
        "10010",
        "10001",
    ),
    "L": (
        "10000",
        "10000",
        "10000",
        "10000",
        "10000",
        "10000",
        "11111",
    ),
    "M": (
        "10001",
        "11011",
        "10101",
        "10101",
        "10001",
        "10001",
        "10001",
    ),
    "N": (
        "10001",
        "11001",
        "10101",
        "10011",
        "10001",
        "10001",
        "10001",
    ),
    "O": (
        "01110",
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "01110",
    ),
    "P": (
        "11110",
        "10001",
        "10001",
        "11110",
        "10000",
        "10000",
        "10000",
    ),
    "Q": (
        "01110",
        "10001",
        "10001",
        "10001",
        "10101",
        "10010",
        "01101",
    ),
    "R": (
        "11110",
        "10001",
        "10001",
        "11110",
        "10100",
        "10010",
        "10001",
    ),
    "S": (
        "01111",
        "10000",
        "10000",
        "01110",
        "00001",
        "00001",
        "11110",
    ),
    "T": (
        "11111",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
        "00100",
    ),
    "U": (
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "01110",
    ),
    "V": (
        "10001",
        "10001",
        "10001",
        "10001",
        "10001",
        "01010",
        "00100",
    ),
    "W": (
        "10001",
        "10001",
        "10001",
        "10101",
        "10101",
        "10101",
        "01010",
    ),
    "X": (
        "10001",
        "10001",
        "01010",
        "00100",
        "01010",
        "10001",
        "10001",
    ),
    "Y": (
        "10001",
        "10001",
        "01010",
        "00100",
        "00100",
        "00100",
        "00100",
    ),
    "Z": (
        "11111",
        "00001",
        "00010",
        "00100",
        "01000",
        "10000",
        "11111",
    ),
}


@dataclass(frozen=True, slots=True)
class TextSpan:
    """A contiguous section of text with one RGB foreground color."""

    text: str
    color: Color


@dataclass(frozen=True, slots=True)
class RenderedMessage:
    """Rendered text ready for transmission to the LED controller."""

    frames: tuple[RenderedFrame, ...]
    final_frame: RenderedFrame
    content_width: int
    scrolls: bool


def normalize_input_text(text: str) -> str:
    """Normalize stdin payloads into a single display line."""
    if text.endswith("\n"):
        text = text[:-1]
        if text.endswith("\r"):
            text = text[:-1]
    return (
        text.replace("\r\n", "\n")
        .replace("\r", "\n")
        .replace("\n", " ")
        .replace("\t", "    ")
    )


def parse_ansi_text(text: str) -> tuple[TextSpan, ...]:
    """Parse ANSI SGR color sequences into styled text spans."""
    spans: list[TextSpan] = []
    current_color = DEFAULT_COLOR
    cursor = 0

    for match in ANSI_PATTERN.finditer(text):
        if match.start() > cursor:
            spans.append(TextSpan(text[cursor : match.start()], current_color))
        current_color = _apply_sgr(current_color, match.group(1))
        cursor = match.end()

    if cursor < len(text):
        spans.append(TextSpan(text[cursor:], current_color))

    return tuple(_coalesce_spans(spans))


def render_message(text: str) -> RenderedMessage:
    """Render a message string into one or more RGB frames."""
    spans = parse_ansi_text(normalize_input_text(text))
    raster, content_width = _rasterize_spans(spans)

    if content_width <= MATRIX_WIDTH:
        frame = _frame_from_raster(raster, (MATRIX_WIDTH - content_width) // 2)
        return RenderedMessage(
            frames=(frame,),
            final_frame=frame,
            content_width=content_width,
            scrolls=False,
        )

    final_offset = MATRIX_WIDTH - content_width
    frames = tuple(
        _frame_from_raster(raster, offset)
        for offset in range(MATRIX_WIDTH, final_offset - 1, -1)
    )
    final_frame = _frame_from_raster(raster, final_offset)
    return RenderedMessage(
        frames=frames,
        final_frame=final_frame,
        content_width=content_width,
        scrolls=True,
    )


def _apply_sgr(current_color: Color, parameters: str) -> Color:
    codes = [int(part) for part in parameters.split(";") if part] if parameters else [0]
    color = current_color
    index = 0

    while index < len(codes):
        code = codes[index]
        if code == 0 or code == 39:
            color = DEFAULT_COLOR
        elif code in ANSI_COLORS:
            color = ANSI_COLORS[code]
        elif code == 38 and index + 1 < len(codes):
            mode = codes[index + 1]
            if mode == 2 and index + 4 < len(codes):
                color = tuple(codes[index + offset] for offset in (2, 3, 4))
                index += 4
            elif mode == 5 and index + 2 < len(codes):
                color = _xterm_color_to_rgb(codes[index + 2])
                index += 2
        index += 1

    return color


def _coalesce_spans(spans: Iterable[TextSpan]) -> list[TextSpan]:
    merged: list[TextSpan] = []
    for span in spans:
        if not span.text:
            continue
        if merged and merged[-1].color == span.color:
            previous = merged[-1]
            merged[-1] = TextSpan(previous.text + span.text, previous.color)
            continue
        merged.append(span)
    return merged


def _rasterize_spans(spans: Iterable[TextSpan]) -> tuple[list[list[Color]], int]:
    glyphs: list[tuple[tuple[str, ...], int, int, Color]] = []
    content_width = 0

    for span in spans:
        for character in span.text:
            rows = _glyph_for_character(character)
            left, width = _glyph_bounds(rows)
            glyphs.append((rows, left, width, span.color))
            content_width += width

    if glyphs:
        content_width += LETTER_SPACING * (len(glyphs) - 1)

    raster = [[BLACK for _ in range(content_width)] for _ in range(MATRIX_HEIGHT)]
    cursor = 0

    for rows, left, width, color in glyphs:
        for row_index, row in enumerate(rows):
            for column_index in range(width):
                if row[left + column_index] == "1":
                    raster[VERTICAL_OFFSET + row_index][cursor + column_index] = color
        cursor += width + LETTER_SPACING

    return raster, content_width


def _frame_from_raster(raster: list[list[Color]], offset: int) -> RenderedFrame:
    content_width = len(raster[0]) if raster else 0
    rows: list[tuple[Color, ...]] = []

    for row in range(MATRIX_HEIGHT):
        frame_row: list[Color] = []
        for column in range(MATRIX_WIDTH):
            source_column = column - offset
            if 0 <= source_column < content_width:
                frame_row.append(raster[row][source_column])
            else:
                frame_row.append(BLACK)
        rows.append(tuple(frame_row))

    return tuple(rows)


def _glyph_for_character(character: str) -> tuple[str, ...]:
    return GLYPHS.get(character.upper(), GLYPHS["?"])


def _glyph_bounds(rows: tuple[str, ...]) -> tuple[int, int]:
    active_columns = [
        column
        for column in range(len(rows[0]))
        if any(row[column] == "1" for row in rows)
    ]
    if not active_columns:
        return 0, 3
    left = min(active_columns)
    right = max(active_columns)
    return left, right - left + 1


def _xterm_color_to_rgb(color_index: int) -> Color:
    color_index = max(0, min(255, color_index))
    if color_index < 16:
        return {
            0: (0, 0, 0),
            1: (128, 0, 0),
            2: (0, 128, 0),
            3: (128, 128, 0),
            4: (0, 0, 128),
            5: (128, 0, 128),
            6: (0, 128, 128),
            7: (192, 192, 192),
            8: (128, 128, 128),
            9: RED,
            10: GREEN,
            11: YELLOW,
            12: BLUE,
            13: MAGENTA,
            14: CYAN,
            15: WHITE,
        }[color_index]

    if color_index < 232:
        cube_index = color_index - 16
        red_index = cube_index // 36
        green_index = (cube_index % 36) // 6
        blue_index = cube_index % 6
        steps = [0, 95, 135, 175, 215, 255]
        return (steps[red_index], steps[green_index], steps[blue_index])

    gray = 8 + (color_index - 232) * 10
    return (gray, gray, gray)
