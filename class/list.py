import peewee
import sys


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

def fmt_names():
    return sorted(formatters.keys())


sorters = {
    'name': lambda db: db.Student.forename,
    'group': lambda db: db.GroupMembership.id,
    'id': lambda db: db.Student.student_id,
    'level': lambda db: db.Student.graduate_student,
    'username': lambda db: db.Student.username,
}

def sort_names():
    return sorted(sorters.keys())


def print_students(db, csv, filter, sort_by, reverse, details):
    sort_keys = sorted(sorters.keys())
    if sort_by not in sort_keys:
        sys.stderr.write(
            f'Invalid key "{sort_by}" (valid options: {", ".join(sort_keys)})\n')
        sys.exit(1)

    fields = details.split(',')
    f = [formatters[key] for key in fields]

    from . import db
    students = (
            db.Student.select()
                      .join(db.GroupMembership, peewee.JOIN.LEFT_OUTER)
                      .join(db.LabGroup, peewee.JOIN.LEFT_OUTER)
                      .order_by(db.LabGroup.number)
    )

    if filter:
        students = students.where(db.SQL(filter))

    sorter = sorters[sort_by](db)
    if reverse:
        sorter = sorter.desc()

    if csv:
        print(','.join([str(f) for f in fields]))

    for s in students.order_by(sorter):
        print_details(s, f, csv)


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
