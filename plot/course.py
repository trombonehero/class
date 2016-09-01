import numpy


def run(args, db):
    assert args.subject is not None
    assert args.course is not None

    marks = (
        db.TranscriptEntry.select(db.TranscriptEntry.mark)
                          .where(db.TranscriptEntry.mark != None)
                          .where(db.TranscriptEntry.subject == args.subject)
                          .where(db.TranscriptEntry.code == args.course)
    )

    data = numpy.array([ e.mark for e in marks ])

    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(nrows = 2)
    axes[0].set_title('Marks in %s %s' % (args.subject, args.course))

    axes[0].boxplot(data, 0, 'rs', 0)
    axes[0].set_xlim([ 0, 100 ])
    axes[0].grid(True)

    axes[1].hist(data, bins = 20)
    axes[1].set_xlim([ 0, 100 ])
    axes[1].grid(True)

    plt.show()
