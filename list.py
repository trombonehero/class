sort_keys = [ 'name', 'username', 'id' ]

def run(args, db):
    from db import Student

    sorters = {
        'name': Student.forename,
        'username': Student.username,
        'id': Student.student_id,
    }

    students = Student.select()

    for s in students.order_by(sorters[args.sort_by]):
        print('%12s %9s %-24s %20s   Group %2d' % (
            s.username, s.student_id, s.name(), s.email(), s.group()))
