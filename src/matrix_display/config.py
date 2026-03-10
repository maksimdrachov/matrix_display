"""Configuration loading for the matrix_display CLI."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONFIG_PATH = Path.home() / ".matrix_display"


@dataclass(frozen=True, slots=True)
class DisplayTarget:
    """A named matrix display target."""

    target_display: str
    controller_ip: str


@dataclass(frozen=True, slots=True)
class MatrixDisplayConfig:
    """User-provided CLI configuration."""

    displays: tuple[DisplayTarget, ...] = ()


def load_config(path: Path | None = None) -> MatrixDisplayConfig:
    """Load matrix display configuration from TOML."""
    config_path = path or DEFAULT_CONFIG_PATH
    if not config_path.exists():
        return MatrixDisplayConfig()

    with config_path.open("rb") as handle:
        data = tomllib.load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"config at {config_path} must contain a TOML table")

    unknown_keys = sorted(set(data) - {"display"})
    if unknown_keys:
        formatted = ", ".join(unknown_keys)
        raise ValueError(f"unsupported config keys in {config_path}: {formatted}")

    raw_displays = data.get("display", [])
    if not isinstance(raw_displays, list):
        raise ValueError(f"display in {config_path} must be an array of tables")

    displays = tuple(
        _parse_display_target(entry, config_path) for entry in raw_displays
    )
    _validate_unique_target_names(displays, config_path)
    return MatrixDisplayConfig(displays=displays)


def resolve_controller_ip(target_display: str, config_path: Path | None = None) -> str:
    """Resolve the target controller IP from the named display configuration."""
    config = load_config(config_path)
    for display in config.displays:
        if display.target_display == target_display:
            return display.controller_ip

    config_file = config_path or DEFAULT_CONFIG_PATH
    raise ValueError(
        f"target display {target_display!r} was not found in {config_file}"
    )


def _parse_display_target(entry: object, config_path: Path) -> DisplayTarget:
    if not isinstance(entry, dict):
        raise ValueError(f"each display entry in {config_path} must be a TOML table")

    unknown_keys = sorted(set(entry) - {"target_display", "controller_ip"})
    if unknown_keys:
        formatted = ", ".join(unknown_keys)
        raise ValueError(f"unsupported display keys in {config_path}: {formatted}")

    target_display = entry.get("target_display")
    controller_ip = entry.get("controller_ip")
    if not isinstance(target_display, str) or not target_display:
        raise ValueError(f"target_display in {config_path} must be a non-empty string")
    if not isinstance(controller_ip, str) or not controller_ip:
        raise ValueError(f"controller_ip in {config_path} must be a non-empty string")

    return DisplayTarget(
        target_display=target_display,
        controller_ip=controller_ip,
    )


def _validate_unique_target_names(
    displays: tuple[DisplayTarget, ...], config_path: Path
) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for display in displays:
        if display.target_display in seen:
            duplicates.add(display.target_display)
            continue
        seen.add(display.target_display)

    if duplicates:
        formatted = ", ".join(sorted(duplicates))
        raise ValueError(
            f"duplicate target_display values in {config_path}: {formatted}"
        )
