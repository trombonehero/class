#!/usr/bin/env python3

def main():
    import argparse
    import importlib
    import logging

    from . import add
    from . import banner
    from . import config
    from . import group
    from . import list as list_module
    from . import mail
    from . import parse
    from . import passwd
    from . import plot
    from . import svn

    argp = argparse.ArgumentParser()
    argp.add_argument('--db', help = 'database URL', default = config.database)
    argp.add_argument('-v', '--verbose', help = 'log additional information',
                      action='store_true')

    subparsers = argp.add_subparsers(dest = 'command')

    init = subparsers.add_parser('init', help = 'initialize class database')

    add.setup_argparse(
            subparsers.add_parser('add', help = 'add student(s) manually'))

    banner.setup_argparse(
            subparsers.add_parser('banner', help = 'interact directly with Banner'))

    parsesub = subparsers.add_parser('parse', help = 'parse Banner HTML')
    parse.setup_argparse(parsesub)

    l = subparsers.add_parser('list', help = 'list students in the course')
    list_module.setup_argparse(l)

    group.setup_argparse(subparsers.add_parser('group',
            help = 'group students together (e.g., for labs)'))

    passwd.setup_argparse(subparsers.add_parser('passwd',
            help = "manage users' password hashes"))

    svn.setup_argparse(
            subparsers.add_parser('svn', help = 'write SVN configuration'))

    mail.setup_argparse(subparsers.add_parser('mail', help = 'send email to class'))

    plotsub = subparsers.add_parser('plot', help = 'plot statistics')
    plot.setup_argparse(plotsub)

    args = argp.parse_args()


    logging.basicConfig(format='[%(levelname)s]\t%(message)s',
                        level=logging.DEBUG if args.verbose else logging.INFO)

    # Set database URL and open the connection:
    setattr(config, 'database', args.db)
    from . import db

    db.connect()

    if args.command:
        # Import and execute the named command:
        importlib.import_module(args.command).run(args, db)
    else:
        argp.print_usage()

        import sys
        sys.exit(1)

    db.close()


if __name__ == '__main__':
    main()
