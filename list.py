import sys

sort_keys = [ 'name', 'username', 'id' ]


def setup_argparse(parser):
    parser.add_argument('--sort-by', default = sort_keys[0],
        help = 'how to sort students (%s)' % ' | '.join(sort_keys))

    parser.add_argument('details', help = 'details to show for each student',
        nargs = '*', default = [ 'username', 'id', 'name', 'email', 'group' ])


def run(args, db):
    from db import Student

    sorters = {
        'name': Student.forename,
        'username': Student.username,
        'id': Student.student_id,
    }

    formatters = {
        'email': lambda s: '%20s' % s.email(),
        'group': lambda s: 'Group %-2d' % s.group(),
        'id': lambda s: '%9s' % s.student_id,
        'level': lambda s: 'Graduate' if s.graduate_student else 'Undergrad',
        'name': lambda s: '%-24s' % s.name(),
        'username': lambda s: '%12s' % s.username,
    }

    formatters = [ formatters[key] for key in args.details ]

    students = Student.select()

    for s in students.order_by(sorters[args.sort_by]):
        print_details(s, formatters)


def print_details(student, formatters):
    for f in formatters:
        sys.stdout.write(f(student))
        sys.stdout.write(' ')

    sys.stdout.write('\n')
