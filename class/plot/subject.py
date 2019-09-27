import collections
import numpy


def run(args, db):
    assert args.subject is not None

    marks = (
        db.TranscriptEntry.select()
                          .where(db.TranscriptEntry.mark != None)
                          .where(db.TranscriptEntry.subject == args.subject)
    )

    data = collections.defaultdict(list)
    for e in marks:
        data[e.code].append(e.mark)

    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(ncols = len(data))
    plt.title('Marks in all %s courses' % args.subject)

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
