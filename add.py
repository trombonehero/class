def setup_argparse(parser):
    pass


def run(args, db):
    try:
        while True:
            add_user(db)

    except EOFError:
        return


def add_user(db):
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
