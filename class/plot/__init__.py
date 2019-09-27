import importlib

def setup_argparse(parser):
    subparsers = parser.add_subparsers(dest = 'plot_command')

    course = subparsers.add_parser('course', help = 'marks in a prerequisite')
    course.add_argument('subject', help = 'academic subject (e.g., ENGI)')
    course.add_argument('course', help = 'course number (e.g., 3891)')

    subject = subparsers.add_parser('subject', help = 'marks in a prerequisite')
    subject.add_argument('subject', help = 'academic subject (e.g., ENGI)')

    subparsers.add_parser('eng-one', help = 'marks in Engineering One')


def run(args, db):
    command = 'plot.' + args.plot_command
    importlib.import_module(command).run(args, db)
