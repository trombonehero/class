import click


@click.group('plot')
def cli():
    """Plot statistics (student grades, etc.)."""



@cli.command()
@click.argument('subject', required=True)
@click.argument('course_code', required=True)
@click.pass_obj
def course(db, subject, course_code):
    """Plot all students' marks in a specific course."""

    import matplotlib.pyplot as plt
    import numpy

    marks = (
        db.TranscriptEntry.select(db.TranscriptEntry.mark)
                          .where(db.TranscriptEntry.mark != None)
                          .where(db.TranscriptEntry.subject == subject)
                          .where(db.TranscriptEntry.code == course_code)
    )

    data = numpy.array([e.mark for e in marks])

    fig, axes = plt.subplots(nrows = 2)
    axes[0].set_title('Marks in %s %s' % (subject, course_code))

    axes[0].boxplot(data, 0, 'rs', 0)
    axes[0].set_xlim([ 0, 100 ])
    axes[0].grid(True)

    axes[1].hist(data, bins = 20)
    axes[1].set_xlim([ 0, 100 ])
    axes[1].grid(True)

    plt.show()


@cli.command()
@click.argument('subject', required=True)
@click.pass_obj
def subject(db, subject):
    """Parse grades in all courses in a subject."""

    import collections
    import matplotlib.pyplot as plt
    import numpy

    marks = (
        db.TranscriptEntry.select()
                          .where(db.TranscriptEntry.mark != None)
                          .where(db.TranscriptEntry.subject == subject)
    )

    data = collections.defaultdict(list)
    for e in marks:
        data[e.code].append(e.mark)

    fig, axes = plt.subplots(ncols = len(data))
    plt.title('Marks in all %s courses' % subject)

    items = sorted(data.items(), key = lambda c_m: c_m[0])
    for i, (course, marks) in enumerate(items):
        axes[i].boxplot(marks)
        axes[i].set_ylim([ 0, 100 ])
        axes[i].set_xlabel(course)
        axes[i].grid(True)

        if i != 0:
            axes[i].set_yticks([])

    plt.xlabel('Mark')

    plt.show()


@cli.command()
@click.pass_obj
def eng_one(db):
    """Plot marks in all Engineering One courses."""

    import collections

    Entry = db.TranscriptEntry

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
            previous = pb[course] if course in pb else 0
            pb[course] = e.mark if e.mark > previous else previous


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

    items = sorted(courses.items(), key = lambda course,m: course)
    for i, ((subject,course), marks) in enumerate(items):
        axes = plt.subplot2grid(dimensions, (2, i), rowspan = 3)
        axes.boxplot(marks)
        axes.set_ylim([ 0, 100 ])
        axes.set_xlabel('%s %s' % (subject, course))
        axes.grid(True)

    plt.show()
