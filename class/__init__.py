#!/usr/bin/env python3

import click
import sys

#from . import add
#from . import banner
#from . import config
#from . import group
from . import list as lst
#from . import mail
#from . import parse
#from . import passwd
#from . import plot
#from . import svn


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
        sys.stderr.write('Error: %s\n' % e)
        sys.exit(1)

    except e:
        raise e


@cli.command()
@click.pass_context
@click.option('--csv', help='output in CSV format', is_flag=True)
@click.option('--filter', help='SQL filter to apply')
@click.option('--sort-by', default='name',
              help='how to sort students' +
                   f' (any of: {", ".join(lst.sort_names())})')
@click.option('--reverse', help='sort in reverse order', is_flag=True)
@click.option('--details', default='username,id,name,email,group',
              help='what to print about each student' +
                   f' (comma-separated list of: {", ".join(lst.fmt_names())})')
def list(ctx, csv, filter, sort_by, reverse, details):
    """List students in the course."""

    from . import db

    lst.print_students(db, csv, filter, sort_by, reverse, details)


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
#    add.setup_argparse(
#            subparsers.add_parser('add', help = 'add student(s) manually'))
#
#    banner.setup_argparse(
#            subparsers.add_parser('banner', help = 'interact directly with Banner'))
#
#    parsesub = subparsers.add_parser('parse', help = 'parse Banner HTML')
#    parse.setup_argparse(parsesub)
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
