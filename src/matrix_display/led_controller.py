"""Art-Net LED controller for the 10x118 matrix."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Protocol

from ._vendor import ensure_stupidartnet_on_path

ensure_stupidartnet_on_path()

from stupidArtnet import StupidArtnet

MATRIX_HEIGHT = 10
MATRIX_WIDTH = 118
CHANNELS_PER_PIXEL = 3
PIXELS_PER_OUTPUT = MATRIX_WIDTH
DMX_CHANNELS_PER_OUTPUT = PIXELS_PER_OUTPUT * CHANNELS_PER_PIXEL
DEFAULT_TARGET_IP = "192.168.1.201"
DEFAULT_UNIVERSES = tuple(range(1, MATRIX_HEIGHT + 1))

RgbPixel = tuple[int, int, int]
ScalarPixel = int | bool
Pixel = ScalarPixel | Sequence[int]
Frame = Sequence[Sequence[Pixel]]


class ArtNetClient(Protocol):
    """Subset of the stupidArtnet client used by the controller."""

    def send(self, packet: bytearray) -> None:
        """Transmit a DMX packet."""

    def close(self) -> None:
        """Release socket resources."""


ArtNetClientFactory = Callable[[str, int, int, int], ArtNetClient]


@dataclass(slots=True)
class LedController:
    """Send 10x118 frames to the PixLite via 10 Art-Net universes."""

    target_ip: str = DEFAULT_TARGET_IP
    universes: Sequence[int] | None = None
    fps: int = 30
    mirror_x: bool = True
    artnet_client_factory: ArtNetClientFactory | None = None
    _clients: tuple[ArtNetClient, ...] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.universes = tuple(self.universes or DEFAULT_UNIVERSES)
        if len(self.universes) != MATRIX_HEIGHT:
            raise ValueError(
                f"expected {MATRIX_HEIGHT} universes, got {len(self.universes)}"
            )
        factory = self.artnet_client_factory or _default_artnet_client_factory
        self._clients = tuple(
            factory(self.target_ip, universe, DMX_CHANNELS_PER_OUTPUT, self.fps)
            for universe in self.universes
        )

    def push_frame(self, frame: Frame) -> tuple[bytearray, ...]:
        """Validate, serialize, and transmit one frame."""
        payloads = self.serialize_frame(frame)
        for client, payload in zip(self._clients, payloads, strict=True):
            client.send(payload)
        return payloads

    def serialize_frame(self, frame: Frame) -> tuple[bytearray, ...]:
        """Convert a 10x118 frame into per-output RGB DMX payloads."""
        if len(frame) != MATRIX_HEIGHT:
            raise ValueError(f"expected {MATRIX_HEIGHT} rows, got {len(frame)}")

        payloads: list[bytearray] = []
        for row_index, row in enumerate(frame):
            if len(row) != MATRIX_WIDTH:
                raise ValueError(
                    f"expected {MATRIX_WIDTH} columns in row {row_index}, got {len(row)}"
                )
            payload = bytearray()
            pixels = reversed(row) if self.mirror_x else row
            for pixel in pixels:
                payload.extend(_normalize_pixel(pixel))
            payloads.append(payload)
        return tuple(payloads)

    def close(self) -> None:
        """Close the underlying Art-Net clients."""
        for client in self._clients:
            client.close()


def make_calibration_frame() -> tuple[tuple[int, ...], ...]:
    """Build a 10-row version of the corner-and-edge calibration pattern."""
    rows = []
    for row_index in range(MATRIX_HEIGHT):
        row = [0] * MATRIX_WIDTH
        if row_index in {0, MATRIX_HEIGHT - 1}:
            row[:5] = [1] * 5
            row[-5:] = [1] * 5
        elif row_index in {1, 2, 3, 6, 7, 8}:
            row[0] = 1
            row[-1] = 1
        rows.append(tuple(row))
    return tuple(rows)


def _default_artnet_client_factory(
    target_ip: str, universe: int, packet_size: int, fps: int
) -> ArtNetClient:
    return StupidArtnet(
        target_ip=target_ip,
        universe=universe,
        packet_size=packet_size,
        fps=fps,
    )


def _normalize_pixel(pixel: Pixel) -> RgbPixel:
    if isinstance(pixel, bool):
        value = 255 if pixel else 0
        return (value, value, value)

    if isinstance(pixel, int):
        if pixel not in range(0, 256):
            raise ValueError(f"pixel intensity {pixel} is outside the 0-255 range")
        value = 255 if pixel == 1 else pixel
        return (value, value, value)

    if len(pixel) != CHANNELS_PER_PIXEL:
        raise ValueError("RGB pixels must contain exactly three channel values")

    channels = tuple(int(channel) for channel in pixel)
    for channel in channels:
        if channel not in range(0, 256):
            raise ValueError(
                f"RGB channel intensity {channel} is outside the 0-255 range"
            )
    return channels  # type: ignore[return-value]
