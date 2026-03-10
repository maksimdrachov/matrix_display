# Matrix Display

`matrix_display` is a CLI tool that can be used to display terminal output on an LED wall.

## Usage

```sh
echo "Some message" | matrix_display --target maksim
```

`matrix_display` reads a message from standard input, renders it with a built-in bitmap
font, and sends the corresponding Art-Net frames directly to the PixLite controller.

If the rendered message fits within `118` pixels, it is centered. If it is wider than
`118` pixels, it scrolls once and then leaves the last visible slice on screen. The
PixLite is expected to be configured to hold the last received frame.

Use the command directly from the repo:

```sh
./matrix_display
```

Or create a symlink somewhere on your `PATH`, for example:

```sh
ln -s ~/matrix_display/matrix_display ~/.local/bin/matrix_display
```

Make sure `~/.local/bin` is on your `PATH`.

If you prefer not to install anything, this also works:

```sh
PYTHONPATH=src python3 -m matrix_display
```

To use `matrix_display`, provide a `~/.matrix_display` config file:

```toml
[[display]]
target_display = "maksim"
controller_ip = "192.168.1.201"

[[display]]
target_display = "meeting_room"
controller_ip = "192.168.1.202"
```

Use `--target` or `-t` to select which configured display to send to:

```sh
echo "Some message" | matrix_display --target maksim
echo "Some message" | matrix_display -t maksim
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
