import click

from . import classlist
from . import transcript


@click.group('parse')
def cli():
    """Parse data from Banner HTML."""


cli.add_command(classlist.cli)
cli.add_command(transcript.cli)
