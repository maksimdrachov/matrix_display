# Matrix Display

Matrix Display is a 10x118 LED matrix display that can be used for displaying messages.

## Usage

The eventual user-facing CLI is intended to work like this:

```sh
echo "Some message" | matrix_display
```

The current implementation provides the Art-Net transport layer and a calibration test for the PixLite 16 MK2.

## Development

`LedController` maps the matrix rows to 10 Art-Net universes, one per output:

- `OUT1` -> row `0` -> universe `1`
- `OUT2` -> row `1` -> universe `2`
- ...
- `OUT10` -> row `9` -> universe `10`

Each output carries `118` RGB pixels (`354` DMX channels).

Run the unit tests:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -t .
```

Display the calibration frame on the controller at `192.168.1.201`:

```sh
MATRIX_DISPLAY_RUN_HARDWARE_TESTS=1 PYTHONPATH=src python3 -m unittest tests.test_calibration
```

You can override the target universes with `MATRIX_DISPLAY_UNIVERSES=1,2,3,4,5,6,7,8,9,10` and the target IP with `MATRIX_DISPLAY_TARGET_IP=192.168.1.201`.
