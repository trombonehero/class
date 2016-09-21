import itertools
import peewee
import sys


def setup_argparse(parser):
    parser.add_argument('--auto', action = 'store_true',
            help = 'automatically group remainder')

    parser.add_argument('students', help = 'students to group together',
            nargs = '*')


def run(args, db):
    from db import GroupMembership, Student

    students = [ Student.get(username = name) for name in args.students ]
    if len(students) > 0:
        create_group(students, db)

    if args.auto:
        group_remainder(db)


def create_group(students, db):
    g = db.LabGroup.create()
    sys.stdout.write('%4d  ' % g.number)

    for s in students:
        sys.stdout.write('  %12s %-20s' % (s.username, s.name()))
        db.GroupMembership.create(group = g, student = s)

    sys.stdout.write('\n')


def group_remainder(db):
    from db import GroupMembership, Student

    ungrouped = (
        Student.select()
               .join(GroupMembership, peewee.JOIN.LEFT_OUTER)
               .where(GroupMembership.student == None)
               .order_by(Student.student_id)
    )

    ugrad_groups = group(ungrouped.where(Student.graduate_student == False))
    grad_groups = group(ungrouped.where(Student.graduate_student == True))

    groups = list(ugrad_groups) + list(grad_groups)
    print('Grouped %d students into %d groups:' % (len(ungrouped), len(groups)))
    for students in groups:
        create_group(students, db)

    print('ungrouped: %d' %
        Student.select(peewee.fn.Count())
               .join(GroupMembership, peewee.JOIN.LEFT_OUTER)
               .where(GroupMembership.student == None)
               .order_by(Student.student_id)
               .scalar()
    )


# Organize students into groups.
def group(students, size = 2):
    args = [ iter(list(students)) ] * size
    return itertools.izip(*args)
