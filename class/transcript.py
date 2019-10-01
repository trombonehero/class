import collections


def setup_argparse(parser):
    parser.add_argument('student', help='student ID or username')


def run(args, db):
    from db import Student, TranscriptEntry as Entry

    id = args.student
    if id.startswith('0') or id.startswith('2'):
        s = Student.get(student_id=int(id))
    else:
        s = Student.get(username=id)

    print('%-20s  %09d  %s' % (s.name(), s.student_id, s.email()))

    for e in Entry.select().where(Entry.student == s.student_id).order_by(Entry.year, Entry.term):
        if e.mark is None:
            continue

        print('%4s %-4s    %04d%02d %3d' % (
            e.subject, e.code, e.year, e.term, e.mark))

#        if (
#                (e.subject == 'CHEM' and e.code == '1050')
#                or (e.subject == 'ENGI' and
#                    (e.code == '1010'
#                     or e.code == '1020'
#                     or e.code == '1030'
#                     or e.code == '1040'))
#                or (e.subject == 'ENGL' and e.code == '1080')
#                or (e.subject == 'MATH' and
#                    (e.code == '1000'
#                     or e.code == '1001'
#                     or e.code == '2050'))
#                or (e.subject == 'PHYS' and
#                    (e.code == '1050'
#                     or e.code == '1051'))
#            ):
#            course = (e.subject, e.code)
#            courses[course].append(e.mark)
#
#            stud_id = e.student.student_id
#            students[stud_id].append(e.mark)
#
#            pb = personal_best[stud_id]
#            previous = pb[course] if course in pb else 0
#            pb[course] = e.mark if e.mark > previous else previous
#
#
#    import matplotlib.pyplot as plt
#
#    dimensions = (5, len(courses))
#
#    plt.subplots(nrows = 5, ncols = len(courses))
#    plt.title('Marks in Engineering One courses')
#
#    histaxes = plt.subplot2grid(dimensions, (0, 0), colspan = len(courses))
#    histaxes.hist([ sum(s) / len(s) for s in students.values() ], bins = 30)
#
#    histaxes = plt.subplot2grid(dimensions, (1, 0), colspan = len(courses))
#    histaxes.hist([
#        sum(s.values()) / len(s.values()) for s in personal_best.values()
#    ], bins = 30)
#
#    items = sorted(courses.items(), key = lambda (course,m): course)
#    for i, ((subject,course), marks) in enumerate(items):
#        axes = plt.subplot2grid(dimensions, (2, i), rowspan = 3)
#        axes.boxplot(marks)
#        axes.set_ylim([ 0, 100 ])
#        axes.set_xlabel('%s %s' % (subject, course))
#        axes.grid(True)
#
#    plt.show()
