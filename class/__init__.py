#!/usr/bin/env python3

import click
import importlib
import pkgutil


@click.group()
@click.option('-d', '--db-url', default='sqlite://class.db')
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose logging.')
@click.pass_context
def cli(ctx, db_url, verbose):
    from . import db

    db.set_url(db_url)
    ctx.obj = db

    import logging
    logging.basicConfig(format='[%(levelname)s]\t%(message)s',
                        level=logging.DEBUG if verbose else logging.INFO)


@cli.command()
@click.pass_obj
def init(db):
    """Initialize a new class database."""

    try:
        db.setup()

    except Exception as e:
        import sys
        sys.stderr.write('Error: %s\n' % e)
        sys.exit(1)

    except e:
        raise e


#
# Add submodules:
#
for module_info in pkgutil.walk_packages(['class']):
    m = importlib.import_module(f'.{module_info.name}', package='class')
    if 'cli' in dir(m):
        cli.add_command(m.cli)


if __name__ == '__main__':
    cli()
