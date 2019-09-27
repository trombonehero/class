import peewee
import sys

from . import db


formatters = {
    'email': lambda s: '%20s' % s.email(),
    'fullmail': lambda s: '%s <%s>' % (s.name(), s.email()),
    'group': lambda s: (
        'Group %-2d' % s.group().number if s.group() else '(no group)'
    ),
    'id': lambda s: '%9s' % s.student_id,
    'level': lambda s: 'Graduate' if s.graduate_student else 'Undergrad',
    'name': lambda s: '%-24s' % s.name(),
    'username': lambda s: '%12s' % s.username,
}

sorters = {
    'name': db.Student.forename,
    'group': db.GroupMembership.id,
    'id': db.Student.student_id,
    'level': db.Student.graduate_student,
    'username': db.Student.username,
}


def setup_argparse(parser):
    parser.add_argument('--csv', action = 'store_true',
        help = 'Output data in CSV format')

    parser.add_argument('--filter', help = 'SQL filter to apply')

    parser.add_argument('--sort-by', default = list(sorters.keys())[0],
        help = 'how to sort students (%s)' % ' | '.join(sorters.keys()))

    parser.add_argument('--reverse', action = 'store_true',
        help = 'sort class list in reverse')

    parser.add_argument('details',
            help = 'details to show for each student (possible details: %s)' %
                ', '.join(sorted(formatters.keys())),
        nargs = '*', default = [ 'username', 'id', 'name', 'email', 'group' ])


def run(args, db):
    if args.sort_by not in sorters.keys():
        sys.stderr.write("Invalid sort key: '%s'\nValid keys are: %s\n" % (
            args.sort_by, ' '.join(sorters.keys())))
        sys.exit(1)

    f = [ formatters[key] for key in args.details ]

    students = (
            db.Student.select()
                      .join(db.GroupMembership, peewee.JOIN.LEFT_OUTER)
                      .join(db.LabGroup, peewee.JOIN.LEFT_OUTER)
                      .order_by(db.LabGroup.number)
    )

    if args.filter:
        students = students.where(db.SQL(args.filter))

    sorter = sorters[args.sort_by]
    if args.reverse:
        sorter = sorter.desc()

    if args.csv:
        print(','.join([ '%s' % key for key in args.details ]))

    for s in students.order_by(sorter):
        print_details(s, f, args.csv)


def print_details(student, formatters, csv = False):
    line = []

    for f in formatters:
        s = f(student)

        if csv:
            s = s.strip()
            if ' ' in s:
                s = '"%s"' % s

        line.append(s)

    separator = ',' if csv else ' '
    sys.stdout.write(separator.join(line))
    sys.stdout.write('\n')
