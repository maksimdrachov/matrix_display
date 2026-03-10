"""Configuration loading for the matrix_display CLI."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .led_controller import DEFAULT_TARGET_IP

DEFAULT_CONFIG_PATH = Path.home() / ".matrix_display"
TARGET_IP_ENV_VAR = "MATRIX_DISPLAY_TARGET_IP"


@dataclass(frozen=True, slots=True)
class MatrixDisplayConfig:
    """User-provided CLI configuration."""

    controller_ip: str | None = None


def load_config(path: Path | None = None) -> MatrixDisplayConfig:
    """Load matrix display configuration from TOML."""
    config_path = path or DEFAULT_CONFIG_PATH
    if not config_path.exists():
        return MatrixDisplayConfig()

    with config_path.open("rb") as handle:
        data = tomllib.load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"config at {config_path} must contain a TOML table")

    unknown_keys = sorted(set(data) - {"controller_ip"})
    if unknown_keys:
        formatted = ", ".join(unknown_keys)
        raise ValueError(f"unsupported config keys in {config_path}: {formatted}")

    controller_ip = data.get("controller_ip")
    if controller_ip is not None and not isinstance(controller_ip, str):
        raise ValueError(f"controller_ip in {config_path} must be a string")

    return MatrixDisplayConfig(controller_ip=controller_ip)


def resolve_controller_ip(
    cli_value: str | None,
    env: Mapping[str, str] | None = None,
    config_path: Path | None = None,
) -> str:
    """Resolve the target controller IP using CLI/env/config/default precedence."""
    if cli_value:
        return cli_value

    environment = env or {}
    env_value = environment.get(TARGET_IP_ENV_VAR)
    if env_value:
        return env_value

    config = load_config(config_path)
    if config.controller_ip:
        return config.controller_ip

    return DEFAULT_TARGET_IP
