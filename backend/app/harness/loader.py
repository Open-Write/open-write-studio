"""
harness/loader.py — load the domains/roles registry (domains.yaml).

Pure data access; the router composes this with provider resolution. The
registry ships alongside this module and may be overridden by an env var for
testing.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

REGISTRY_PATH = Path(os.environ.get(
    "OWS_HARNESS_REGISTRY",
    Path(__file__).resolve().parent / "domains.yaml",
))


@lru_cache(maxsize=1)
def load_registry() -> dict[str, Any]:
    with REGISTRY_PATH.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data


def domains() -> dict[str, Any]:
    return load_registry().get("domains", {})


def roles() -> dict[str, Any]:
    return load_registry().get("roles", {})


def known_domains() -> list[str]:
    return list(domains().keys())


def known_roles() -> list[str]:
    return list(roles().keys())
