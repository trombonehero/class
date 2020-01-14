import click


@click.command('group',
               help='Create lab groups from usernames.')
@click.argument('usernames', nargs=-1, required=True)
@click.option('-a', '--auto', is_flag=True,
              help='Auto-group all ungrouped students')
@click.pass_obj
def cli(db, usernames, auto):
    students = [db.Student.lookup(u) for u in usernames]
    if len(students) > 0:
        create_group(students, db)

    if auto:
        group_remainder(db)


def create_group(students, db):
    import sys

    g = db.LabGroup.create()
    sys.stdout.write('%4d  ' % g.number)

    for s in students:
        sys.stdout.write('  %12s %-20s' % (s.username, s.name()))
        db.GroupMembership.create(group=g, student=s)

    sys.stdout.write('\n')


def group_remainder(db):
    import peewee

    ungrouped = (
        db.Student.select()
                  .join(db.GroupMembership, peewee.JOIN.LEFT_OUTER)
                  .where(db.GroupMembership.student == None)
                  .order_by(db.Student.student_id)
    )

    ugrad_groups = group(ungrouped.where(db.Student.graduate_student == False))
    grad_groups = group(ungrouped.where(db.Student.graduate_student == True))

    groups = list(ugrad_groups) + list(grad_groups)
    print(f'Grouped {len(ungrouped)} students into {len(groups)} groups:')
    for students in groups:
        create_group(students, db)

    print('ungrouped: %d' %
          db.Student.select(peewee.fn.Count())
          .join(db.GroupMembership, peewee.JOIN.LEFT_OUTER)
          .where(db.GroupMembership.student == None)
          .order_by(db.Student.student_id)
          .scalar())


# Organize students into groups.
def group(students, size=2):
    args = [iter(list(students))] * size
    return zip(*args)
