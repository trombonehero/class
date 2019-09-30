import click

from . import classlist
from . import transcript


@click.group()
@click.pass_context
def parse(ctx):
    """Parse data from Banner HTML."""


parse.add_command(classlist.cli)
parse.add_command(transcript.cli)
