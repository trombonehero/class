#!/usr/bin/env python3

import click
import importlib


@click.group()
@click.pass_context
@click.option('-d', '--db', default='sqlite://class.db')
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose logging.')
def cli(ctx, db, verbose):
    ctx.ensure_object(dict)
    ctx.obj['DATABASE_URL'] = db

    import logging
    logging.basicConfig(format='[%(levelname)s]\t%(message)s',
                        level=logging.DEBUG if verbose else logging.INFO)


@cli.command()
@click.pass_context
def init(ctx):
    """Initialize a new class database."""

    try:
        from . import db
        db.setup()

    except Exception as e:
        import sys
        sys.stderr.write('Error: %s\n' % e)
        sys.exit(1)

    except e:
        raise e


#from . import banner
#from . import config
#from . import plot


for name in ('add', 'group', 'list', 'mail', 'parse', 'passwd', 'svn'):
    module = importlib.import_module(f'.{name}', package='class')
    cli.add_command(module.cli)


#def main():
#    import argparse
#    import importlib
#
#
#    argp = argparse.ArgumentParser()
#    banner.setup_argparse(
#            subparsers.add_parser('banner', help = 'interact directly with Banner'))
#
#    plotsub = subparsers.add_parser('plot', help = 'plot statistics')
#    plot.setup_argparse(plotsub)
#
#    args = argp.parse_args()
#
#    # Set database URL and open the connection:
#    setattr(config, 'database', args.db)
#    from . import db
#
#    db.connect()
#    db.close()


if __name__ == '__main__':
    cli()
