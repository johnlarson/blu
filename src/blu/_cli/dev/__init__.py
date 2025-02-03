import asyncio
import click

from blu._utils.asyncio import to_sync
from blu._utils import get_available_port


@click.command()
@to_sync
async def dev():
    proc = await asyncio.create_subprocess_exec(
        'uvicorn',
        '--port', str(get_available_port()),
        '--reload',
        'blu._cli.dev.cli_dev_app:app',
    )
    await proc.wait()