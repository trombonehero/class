import click


@click.command('add')
@click.option('--instructor', is_flag=True,
              help='Is this person a TA or instructor (vs a student)?')
@click.pass_context
def cli(ctx, instructor):
    """Add a student or instructor/TA to the class."""

    from . import db

    if instructor:
        add_instructor(db)
        return

    try:
        while True:
            add_student(db)

    except EOFError:
        return


def add_instructor(db):
    username = prompt('Username')
    inst = db.Instructor(username=username)

    inst.name = prompt('Name')
    inst.ta = prompt('TA [y/N]').lower() == 'y'
    inst.save(force_insert=True)

    print('Added %s' % inst)


def add_student(db):
    student_id = prompt('Student ID')
    s = db.Student(student_id=student_id)

    s.username = prompt('Username')
    s.forename = prompt('Forename')
    s.surname = prompt('Surname')
    s.graduate_student = prompt('Graduate student [y/N]').lower() == 'y'

    # Since Student has a custom primary key (the student ID), we need
    # to force the use of INSERT on our first call to save()
    s.save(force_insert=True)

    print('Added %s' % s)


def prompt(msg):
    while True:
        s = input('%-24s' % (msg + ':'))
        if len(s) > 0:
            return s
