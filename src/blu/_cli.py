import asyncio
import subprocess

from blu._utils import get_available_port


def cli():
    _run_server()


def _run_server():
    proc = subprocess.Popen(
        [
            "uvicorn",
            "--port",
            str(get_available_port()),
            "--reload",
            "blu:app",
        ],
    )
    return proc


def cli_other():
    asyncio.run(_run_server())
