from db import Student
import sys

formatters = {
    'email': lambda s: '%20s' % s.email(),
    'group': lambda s: 'Group %-2d' % s.group(),
    'id': lambda s: '%9s' % s.student_id,
    'level': lambda s: 'Graduate' if s.graduate_student else 'Undergrad',
    'name': lambda s: '%-24s' % s.name(),
    'username': lambda s: '%12s' % s.username,
}

sorters = {
    'name': Student.forename,
    'username': Student.username,
    'id': Student.student_id,
}


def setup_argparse(parser):
    parser.add_argument('--sort-by', default = sorters.keys()[0],
        help = 'how to sort students (%s)' % ' | '.join(sorters.keys()))

    parser.add_argument('details',
            help = 'details to show for each student (possible details: %s)' %
                ', '.join(sorted(formatters.keys())),
        nargs = '*', default = [ 'username', 'id', 'name', 'email', 'group' ])


def run(args, db):
    f = [ formatters[key] for key in args.details ]

    students = Student.select()

    for s in students.order_by(sorters[args.sort_by]):
        print_details(s, f)


def print_details(student, formatters):
    for f in formatters:
        sys.stdout.write(f(student))
        sys.stdout.write(' ')

    sys.stdout.write('\n')
