import collections
import numpy


def run(args, db):
    from db import TranscriptEntry as Entry

    data = collections.defaultdict(list)

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
            data[(e.subject, e.code)].append(e.mark)


    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(ncols = len(data))
    plt.title('Marks in Engineering One courses')

    items = sorted(data.items(), key = lambda (course,m): course)
    for i, ((subject,course), marks) in enumerate(items):
        axes[i].boxplot(marks)
        axes[i].set_ylim([ 0, 100 ])
        axes[i].set_xlabel('%s %s' % (subject, course))
        axes[i].grid(True)

    plt.show()

