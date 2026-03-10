"""Unit tests for the LED controller."""

from __future__ import annotations

import unittest

from matrix_display.led_controller import (
    DMX_CHANNELS_PER_OUTPUT,
    MATRIX_HEIGHT,
    MATRIX_WIDTH,
    LedController,
    make_calibration_frame,
)


class FakeArtNetClient:
    """Minimal test double that records Art-Net payloads."""

    def __init__(
        self, target_ip: str, universe: int, packet_size: int, fps: int
    ) -> None:
        self.target_ip = target_ip
        self.universe = universe
        self.packet_size = packet_size
        self.fps = fps
        self.sent_packets: list[bytearray] = []
        self.closed = False

    def send(self, packet: bytearray) -> None:
        self.sent_packets.append(bytearray(packet))

    def close(self) -> None:
        self.closed = True


class LedControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.created_clients: list[FakeArtNetClient] = []

        def factory(
            target_ip: str, universe: int, packet_size: int, fps: int
        ) -> FakeArtNetClient:
            client = FakeArtNetClient(target_ip, universe, packet_size, fps)
            self.created_clients.append(client)
            return client

        self.controller = LedController(artnet_client_factory=factory)

    def tearDown(self) -> None:
        self.controller.close()

    def test_push_frame_expands_binary_calibration_pixels_to_rgb(self) -> None:
        payloads = self.controller.push_frame(make_calibration_frame())

        self.assertEqual(MATRIX_HEIGHT, len(payloads))
        for payload in payloads:
            self.assertEqual(DMX_CHANNELS_PER_OUTPUT, len(payload))

        top_row = payloads[0]
        self.assertEqual(bytearray([255] * 15), top_row[:15])
        self.assertEqual(
            bytearray([0] * (DMX_CHANNELS_PER_OUTPUT - 30)), top_row[15:-15]
        )
        self.assertEqual(bytearray([255] * 15), top_row[-15:])

        blank_row = payloads[4]
        self.assertEqual(bytearray(DMX_CHANNELS_PER_OUTPUT), blank_row)

        edge_row = payloads[1]
        self.assertEqual(bytearray([255, 255, 255]), edge_row[:3])
        self.assertEqual(bytearray([255, 255, 255]), edge_row[-3:])
        self.assertEqual(
            bytearray([0] * (DMX_CHANNELS_PER_OUTPUT - 6)),
            edge_row[3:-3],
        )

        self.assertEqual(1, len(self.created_clients[0].sent_packets))
        self.assertEqual(top_row, self.created_clients[0].sent_packets[0])

    def test_push_frame_accepts_explicit_rgb_pixels(self) -> None:
        row = [(0, 0, 0)] * MATRIX_WIDTH
        mutable_row = list(row)
        mutable_row[0] = (255, 32, 16)
        frame = tuple(tuple(mutable_row) for _ in range(MATRIX_HEIGHT))

        payloads = self.controller.push_frame(frame)

        self.assertEqual(bytearray([255, 32, 16]), payloads[0][:3])

    def test_push_frame_rejects_wrong_row_count(self) -> None:
        frame = [
            tuple(0 for _ in range(MATRIX_WIDTH)) for _ in range(MATRIX_HEIGHT - 1)
        ]

        with self.assertRaisesRegex(ValueError, "expected 10 rows"):
            self.controller.push_frame(frame)

    def test_push_frame_rejects_wrong_column_count(self) -> None:
        frame = [tuple(0 for _ in range(MATRIX_WIDTH)) for _ in range(MATRIX_HEIGHT)]
        frame[0] = tuple(0 for _ in range(MATRIX_WIDTH - 1))

        with self.assertRaisesRegex(ValueError, f"expected {MATRIX_WIDTH} columns"):
            self.controller.push_frame(frame)

    def test_close_closes_all_artnet_clients(self) -> None:
        self.controller.close()

        self.assertTrue(all(client.closed for client in self.created_clients))


if __name__ == "__main__":
    unittest.main()
