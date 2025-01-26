import asyncio
import click

from blu._utils.asyncio import syncify
from blu._utils import get_available_port


@click.command()
@syncify
async def dev():
    proc = await asyncio.create_subprocess_exec(
        'uvicorn',
        '--port', str(get_available_port()),
        '--reload',
        'blu._cli.dev.cli_dev_app:app',
    )
    await proc.wait()