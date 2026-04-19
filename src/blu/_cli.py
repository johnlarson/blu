import asyncio
import os
import subprocess
import sys
import uvicorn

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


async def _run_server_async():
    config = uvicorn.Config("blu:app", port=get_available_port(), reload=True)
    server = uvicorn.Server(config)
    await server.serve()


async def _run_server_3():
    proc = await asyncio.create_subprocess_exec(
        "uvicorn",
        "--port",
        str(get_available_port()),
        "--reload",
        "blu:app",
        cwd=os.getcwd(),
        env={
            "PYTHONPATH": ":".join(sys.path),
        },
    )
    try:
        await proc.wait()
    except asyncio.CancelledError:
        proc.kill()
