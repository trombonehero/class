import importlib


def setup_argparse(parser):
    subparsers = parser.add_subparsers(dest = 'passwd_command')

    subcommands = {
        'init': 'initialized unset passwords',
        'reset': 'reset user passwords',
    }

    for (name, description) in subcommands.items():
        mod = importlib.import_module(f'.{name}', package='class.passwd')
        mod.setup_argparse(subparsers.add_parser(name, help = description))


def run(args, db):
    command = 'passwd.' + args.passwd_command
    importlib.import_module(command).run(args, db)
