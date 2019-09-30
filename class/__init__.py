#!/usr/bin/env python3

import click

@click.group()
@click.pass_context
@click.option('-d', '--db', default='sqlite://class.db')
def cli(ctx, db):
    ctx.ensure_object(dict)
    ctx.obj['DATABASE_URL'] = db


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


from . import add
cli.add_command(add.cli)

#from . import banner
#from . import config
#from . import group

from . import list as lst
cli.add_command(lst.cli)

#from . import mail

from . import parse
cli.add_command(parse.parse)

#from . import passwd
#from . import plot
#from . import svn


#def main():
#    import argparse
#    import importlib
#    import logging
#
#
#    argp = argparse.ArgumentParser()
#    argp.add_argument('-v', '--verbose', help = 'log additional information',
#                      action='store_true')
#
#    banner.setup_argparse(
#            subparsers.add_parser('banner', help = 'interact directly with Banner'))
#
#    group.setup_argparse(subparsers.add_parser('group',
#            help = 'group students together (e.g., for labs)'))
#
#    passwd.setup_argparse(subparsers.add_parser('passwd',
#            help = "manage users' password hashes"))
#
#    svn.setup_argparse(
#            subparsers.add_parser('svn', help = 'write SVN configuration'))
#
#    mail.setup_argparse(subparsers.add_parser('mail', help = 'send email to class'))
#
#    plotsub = subparsers.add_parser('plot', help = 'plot statistics')
#    plot.setup_argparse(plotsub)
#
#    args = argp.parse_args()
#
#
#    logging.basicConfig(format='[%(levelname)s]\t%(message)s',
#                        level=logging.DEBUG if args.verbose else logging.INFO)
#
#    # Set database URL and open the connection:
#    setattr(config, 'database', args.db)
#    from . import db
#
#    db.connect()
#    db.close()


if __name__ == '__main__':
    cli()
