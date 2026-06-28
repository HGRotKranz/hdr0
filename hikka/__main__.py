"""Entry point. Checks for user and starts main script"""

# ©️ Dan Gazizullin, 2021-2023
# This file is a part of Hikka Userbot
# 🌐 https://github.com/Splaueef/hikka
# You can redistribute it and/or modify it under the terms of the GNU AGPLv3
# 🔑 https://www.gnu.org/licenses/agpl-3.0.html

import getpass
import importlib
import os
import re
import subprocess
import sys
import sysconfig

REQUIREMENTS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
)

MIN_PYTHON_VERSION = (3, 11, 0)
MAX_PYTHON_VERSION = (3, 12, 0)

CONFLICTING_PACKAGES = (
    "telethon",
    "telethon-mod",
    "hikka-tl",
    "hikka-tl-new",
    "hikka-pyro",
    "hikka-pyro-new",
)

REQUIRED_CORE_PACKAGES = (
    ("hikkatl", "2.0.8", "Hikka-TL"),
    ("hikkapyro", "2.0.103", "Hikka-Pyro"),
    ("aiogram", "2.25.2", "aiogram"),
    ("pyrogram", "2.0.106", "Pyrogram"),
)


if (
    getpass.getuser() == "root"
    and "--root" not in " ".join(sys.argv)
    and all(trigger not in os.environ for trigger in {"DOCKER", "GOORM"})
):
    print("🚫" * 15)
    print("You attempted to run Hikka on behalf of root user")
    print("Please, create a new user and restart script")
    print("If this action was intentional, pass --root argument instead")
    print("🚫" * 15)
    print()
    print("Type force_insecure to ignore this warning")
    if input("> ").lower() != "force_insecure":
        sys.exit(1)


def _version_tuple(version: str) -> tuple:
    """Convert package version string to a comparable integer tuple."""
    return tuple(int(part) for part in re.findall(r"\d+", version.split("+", 1)[0]))


def _is_outdated(installed: str, required: str) -> bool:
    """Return True when installed version is older than the required version."""
    return _version_tuple(installed) < _version_tuple(required)


def _assert_core_packages():
    """Ensure core Hikka runtime packages match the supported API versions."""
    for module_name, required_version, display_name in REQUIRED_CORE_PACKAGES:
        module = importlib.import_module(module_name)
        installed_version = getattr(module, "__version__", "0")

        if _is_outdated(installed_version, required_version):
            raise ImportError(
                f"{display_name} {installed_version} is installed, "
                f"but Hikka requires at least {required_version}"
            )


def _format_version(version: tuple) -> str:
    return ".".join(map(str, version))


def _python_headers_available() -> bool:
    """Return True when Python development headers are available for builds."""
    include_dir = sysconfig.get_path("include")
    return bool(include_dir and os.path.exists(os.path.join(include_dir, "Python.h")))


def _print_python_headers_hint():
    print(
        "🚫 Python development headers were not found. "
        "Some dependencies need them when wheels are unavailable for your Python."
    )
    print("Install the headers for your exact Python version, then retry.")
    print("Debian/Ubuntu: sudo apt install python3-dev build-essential")
    print("Fedora: sudo dnf install python3-devel gcc")
    print("Arch: sudo pacman -S python base-devel")


def deps():
    if not _python_headers_available():
        _print_python_headers_hint()

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "uninstall",
            "-y",
            *CONFLICTING_PACKAGES,
        ],
        check=False,
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "-q",
            "--disable-pip-version-check",
            "--no-warn-script-location",
            "-r",
            REQUIREMENTS_PATH,
        ],
        check=True,
    )


def restart():
    from ._internal import restart as _restart

    _restart()


if sys.version_info < MIN_PYTHON_VERSION:
    print(
        "🚫 Error: you must use at least Python version "
        f"{_format_version(MIN_PYTHON_VERSION)}"
    )
    sys.exit(1)
elif sys.version_info >= MAX_PYTHON_VERSION:
    print(
        "🚫 Error: this Hikka build supports Python "
        f">={_format_version(MIN_PYTHON_VERSION)}, <{_format_version(MAX_PYTHON_VERSION)}. "
        "Please use Python 3.11."
    )
    sys.exit(1)
elif __package__ != "hikka":  # In case they did python __main__.py
    print("🚫 Error: you cannot run this as a script; you must execute as a package")
else:
    try:
        _assert_core_packages()
    except Exception:
        print("🔄 Installing dependencies...")
        deps()
        restart()

    try:
        from . import log

        log.init()

        from . import main
    except ImportError as e:
        print(f"{str(e)}\n🔄 Attempting dependencies installation... Just wait ⏱")
        deps()
        restart()

    if "HIKKA_DO_NOT_RESTART" in os.environ:
        del os.environ["HIKKA_DO_NOT_RESTART"]

    main.hikka.main()  # Execute main function
