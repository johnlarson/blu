#!/usr/bin/env python3
"""Profile one ASGI request against an app under tests/apps using yappi."""

from __future__ import annotations

import argparse
import asyncio
import importlib
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import yappi

from blu._utils import asgi

ROOT = Path(__file__).resolve().parents[1]
APPS_DIR = ROOT / "tests" / "apps"


async def _receive() -> asgi.ReceiveEvent:
    return {"type": "http.request"}


class _Sender:
    def __init__(self) -> None:
        self.events: list[asgi.SendEvent] = []

    async def __call__(self, event: asgi.SendEvent) -> None:
        self.events.append(event)

    def status(self) -> int | None:
        for event in self.events:
            if event["type"] == "http.response.start":
                return event["status"]
        return None

    def body(self) -> bytes:
        chunks: list[bytes] = []
        for event in self.events:
            if event["type"] == "http.response.body":
                chunks.append(event.get("body", b""))
                if not event.get("more_body", False):
                    break
        return b"".join(chunks)


def _install_app(app_name: str, project_dir: Path) -> None:
    from blu import _app
    from blu._app import _get_app_def, _get_router
    from blu._settings import settings

    src = APPS_DIR / app_name
    if not src.is_dir():
        raise SystemExit(f"App not found: {src}")

    (project_dir / "app").symlink_to(src.resolve())

    importlib.reload(_app)
    for name in [m for m in sys.modules if m == "app" or m.startswith("app.")]:
        del sys.modules[name]

    sys.path.insert(0, str(project_dir))
    os.chdir(project_dir)
    settings.cache_clear()
    _get_app_def.cache_clear()
    _get_router.cache_clear()


async def _asgi_get(path: str) -> _Sender:
    from blu import app

    if "?" in path:
        path, query_str = path.split("?", 1)
        query = query_str.encode("utf-8")
    else:
        query = b""

    sender = _Sender()
    await app(
        {
            "asgi": {
                "version": "1",
                "spec_version": "2.0",
            },
            "path": path,
            "headers": [],
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "query_string": query,
        },
        _receive,
        sender,
    )
    return sender


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Start the Blu ASGI app with a tests/apps definition and profile "
            "one GET request/response cycle with yappi."
        )
    )
    parser.add_argument(
        "app",
        help="App directory under tests/apps (e.g. basic or e2e/routing)",
    )
    parser.add_argument(
        "path",
        help="URL path to request (e.g. / or /foo?bar=1)",
    )
    parser.add_argument(
        "--clock",
        choices=("cpu", "wall"),
        default="cpu",
        help="yappi clock type (default: cpu)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=40,
        metavar="N",
        help="Print only the top N functions by total time (default: 40; 0 = all)",
    )
    parser.add_argument(
        "--name-width",
        type=int,
        default=36,
        metavar="N",
        help="Width of the name column in the stats table (default: 36)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    with TemporaryDirectory() as temp_dir_str:
        project_dir = Path(temp_dir_str)
        _install_app(args.app, project_dir)

        async def _profiled_request() -> _Sender:
            yappi.set_clock_type(args.clock)
            yappi.clear_stats()
            yappi.start()
            try:
                return await _asgi_get(args.path)
            finally:
                yappi.stop()

        sender = asyncio.run(_profiled_request())

        print(f"status: {sender.status()}")
        print(f"body_bytes: {len(sender.body())}")
        print()

        stats = yappi.get_func_stats()
        stats.sort("ttot", "desc")
        if args.limit > 0:
            while len(stats) > args.limit:
                stats.pop()
        stats.print_all(
            columns={
                0: ("name", args.name_width),
                1: ("ncall", 5),
                2: ("tsub", 8),
                3: ("ttot", 8),
                4: ("tavg", 8),
            }
        )


if __name__ == "__main__":
    main()
