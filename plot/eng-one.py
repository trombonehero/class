import collections
import numpy


def run(args, db):
    from db import TranscriptEntry as Entry

    courses = collections.defaultdict(list)
    students = collections.defaultdict(list)
    personal_best = collections.defaultdict(dict)

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
            course = (e.subject, e.code)
            courses[course].append(e.mark)

            stud_id = e.student.student_id
            students[stud_id].append(e.mark)

            pb = personal_best[stud_id]
            current = pb[course] if course in pb else 0
            pb[course] = e.mark if e.mark > current else current


    import matplotlib.pyplot as plt

    dimensions = (5, len(courses))

    plt.subplots(nrows = 5, ncols = len(courses))
    plt.title('Marks in Engineering One courses')

    histaxes = plt.subplot2grid(dimensions, (0, 0), colspan = len(courses))
    histaxes.hist([ sum(s) / len(s) for s in students.values() ], bins = 30)

    histaxes = plt.subplot2grid(dimensions, (1, 0), colspan = len(courses))
    histaxes.hist([
        sum(s.values()) / len(s.values()) for s in personal_best.values()
    ], bins = 30)

    items = sorted(courses.items(), key = lambda (course,m): course)
    for i, ((subject,course), marks) in enumerate(items):
        axes = plt.subplot2grid(dimensions, (2, i), rowspan = 3)
        axes.boxplot(marks)
        axes.set_ylim([ 0, 100 ])
        axes.set_xlabel('%s %s' % (subject, course))
        axes.grid(True)

    plt.show()

