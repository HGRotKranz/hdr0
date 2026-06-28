"""Pyrogram backend compatibility helpers for Hikka."""

# ©️ Dan Gazizullin, 2021-2023
# This file is a part of Hikka Userbot
# 🌐 https://github.com/Splaueef/hikka
# You can redistribute it and/or modify it under the terms of the GNU AGPLv3
# 🔑 https://www.gnu.org/licenses/agpl-3.0.html

import importlib
import importlib.util
import typing

PREFERRED_BACKENDS = ("pyrogram", "hikkapyro")

BACKEND_MODULE = next(
    backend for backend in PREFERRED_BACKENDS if importlib.util.find_spec(backend)
)

_backend = importlib.import_module(BACKEND_MODULE)

Client = _backend.Client
errors = _backend.errors
raw = _backend.raw
types = _backend.types
__version__ = _backend.__version__


def module_name(name: str = "") -> str:
    """Return the active Pyrogram-compatible module name for import hooks."""
    suffix = name[8:] if name.startswith("pyrogram") else name
    return f"{BACKEND_MODULE}{suffix}"


def raw_layer() -> typing.Optional[int]:
    """Return the active Pyrogram raw layer when the backend exposes it."""
    return getattr(getattr(raw, "all", None), "layer", None)
