<div align="center">
  <img src="./images/matrix_display.png" alt="matrix_display">

  <h1>matrix_display</h1>

  <p><em>CLI tool to display terminal output on an LED wall</em></p>

  <p><a href="https://x.com/maksimdrachov/status/2031714045334532190">🎥 Demo video</a></p>

</div>

---



## Hardware

- [Pixlite 16 Mk2](https://www.advateklighting.com/products/shop/pixlite-16-mk2)
- [LED strips](https://www.amazon.de/-/en/SEZO-Individually-Addressable-Non-Waterproof-Decoration/dp/B09N99DJRG)
- [Aluminium profile](https://www.amazon.de/-/en/StarlandLED-aluminium-accessories-perfectly-LightStrip/dp/B07MPX3WHM) 
- [3-wire cable](https://www.amazon.de/BTF-LIGHTING-SK6812RGBW-Electric-Extension-Connection/dp/B07S8CLRLK)
- [3-pin connectors](https://www.amazon.de/BTF-LIGHTING-Connectors-WS2812B-WS2811-20pairs-10-pairs/dp/B01DC0KIT2)
- [Brackets](https://www.printables.com/model/1633891-matrix_display-brackets) (3d-printed)

Note: you could make this significantly cheaper by designing your own LED driver board (which is left as an exercise to the reader).

## Installation

1. Clone the repo:

```sh
git clone git@github.com:maksimdrachov/matrix_display.git ~/matrix_display
```

2. Create a symlink that is on your `PATH`:

```sh
ln -s ~/matrix_display/matrix_display ~/.local/bin/matrix_display
```

Make sure `~/.local/bin` is on your `PATH`.

3. Create a `~/.matrix_display` config file:

```toml
[[display]]
target_display = "maksim"
controller_ip = "192.168.1.201"

[[display]]
target_display = "meeting_room"
controller_ip = "192.168.1.202"
```

4. Send a message:

```sh
echo "Some message" | matrix_display --target maksim
```

## Usage

`matrix_display` reads a message from standard input, renders it with a built-in bitmap
font, and sends the corresponding Art-Net frames directly to the PixLite controller.

If the rendered message fits within `118` pixels, it is centered. If it is wider than
`118` pixels, it scrolls once and then leaves the last visible slice on screen. The
PixLite is expected to be configured to hold the last received frame.

If you prefer not to install anything, this also works:

```sh
PYTHONPATH=src python3 -m matrix_display
```

Use `--target` or `-t` to select which configured display to send to:

```sh
some_command | matrix_display --target maksim
some_command | matrix_display -t maksim
```

ANSI color sequences in stdin are supported. For example:

```sh
printf '\033[31mRED \033[32mGREEN\033[0m\n' | matrix_display -t maksim
```

## Example Usage

Display the current time in 24-hour format once a second:

```sh
#!/bin/sh

while true; do
  date '+%H:%M:%S' | matrix_display -t maksim
  sleep 1
done
```

Watch the latest GitHub Actions run and display a green or red result when it finishes:

```sh
#!/usr/bin/env bash

if gh run watch --exit-status; then
  printf '\033[32mPASSED\033[0m\n' | matrix_display -t maksim
else
  printf '\033[31mFAILED\033[0m\n' | matrix_display -t maksim
fi
```

Display a very long scrolling `ZUBAX` banner and refresh it every few minutes after
the scroll has finished:

```sh
#!/bin/sh

text=$(printf 'ZUBAX %.0s' $(seq 1 100))

while true; do
  printf '\033[31m%s\033[0m\n' "$text" | matrix_display -t maksim
  sleep 2m
done
```

## Development

`LedController` maps the matrix rows to 10 Art-Net universes, one per output:

- `OUT1` -> row `0` -> universe `1`
- `OUT2` -> row `1` -> universe `2`
- ...
- `OUT10` -> row `9` -> universe `10`

Each output carries `118` RGB pixels (`354` DMX channels).
Rows are mirrored during serialization so logical column `0` appears on the left edge
of the physical display.

## Testing

Run the unit tests:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -t .
```

Display the calibration frame on the controller at `192.168.1.201`:

```sh
MATRIX_DISPLAY_RUN_HARDWARE_TESTS=1 PYTHONPATH=src python3 -m unittest tests.test_calibration
```

For the calibration test only, you can override the target universes with
`MATRIX_DISPLAY_UNIVERSES=1,2,3,4,5,6,7,8,9,10` and the controller IP with
`MATRIX_DISPLAY_TARGET_IP=192.168.1.201`.
