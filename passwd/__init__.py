import importlib


def setup_argparse(parser):
    subparsers = parser.add_subparsers(dest = 'passwd_command')

    subcommands = {
        'init': 'initialized unset passwords',
    }

    for (name, description) in subcommands.items():
        importlib.import_module('passwd.' + name).setup_argparse(
                subparsers.add_parser(name, help = description))


def run(args, db):
    command = 'passwd.' + args.passwd_command
    importlib.import_module(command).run(args, db)
