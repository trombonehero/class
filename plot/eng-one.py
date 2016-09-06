import collections
import numpy


def run(args, db):
    from db import TranscriptEntry as Entry

    courses = collections.defaultdict(list)
    students = collections.defaultdict(list)

    for e in Entry.select().where(Entry.mark is not None):
        if e.mark is None:
            continue

        if (
                (e.subject == 'CHEM' and e.code == '1050')
                or (e.subject == 'ENGI' and
                    (e.code == '1010'
                     or e.code == '1020'
                     or e.code == '1030'
                     or e.code == '1040'))
                or (e.subject == 'ENGL' and e.code == '1080')
                or (e.subject == 'MATH' and
                    (e.code == '1000'
                     or e.code == '1001'
                     or e.code == '2050'))
                or (e.subject == 'PHYS' and
                    (e.code == '1050'
                     or e.code == '1051'))
            ):
            courses[(e.subject, e.code)].append(e.mark)
            students[e.student.student_id].append(e.mark)


    import matplotlib.pyplot as plt

    dimensions = (3, len(courses))

    plt.subplots(nrows = 2, ncols = len(courses))
    plt.title('Marks in Engineering One courses')

    histaxes = plt.subplot2grid(dimensions, (0, 0), colspan = len(courses))
    histaxes.hist([ sum(s) / len(s) for s in students.values() ], bins = 30)

    items = sorted(courses.items(), key = lambda (course,m): course)
    for i, ((subject,course), marks) in enumerate(items):
        axes = plt.subplot2grid(dimensions, (1, i), rowspan = 2)
        axes.boxplot(marks)
        axes.set_ylim([ 0, 100 ])
        axes.set_xlabel('%s %s' % (subject, course))
        axes.grid(True)

    plt.show()

