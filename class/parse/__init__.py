import importlib


def setup_argparse(parser):
    subparsers = parser.add_subparsers(dest = 'banner_command')

    classlist = subparsers.add_parser('classlist', help = 'summary class list')
    classlist.add_argument('file', nargs = '+', help = 'summary class list(s)')

    trans = subparsers.add_parser('transcript', help = 'student transcript')
    trans.add_argument('file', help = 'student transcript')


def run(args, db):
    command = 'parse.' + args.banner_command
    importlib.import_module(command).run(args, db)
