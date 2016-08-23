import peewee
import sys


def run(args, db):
    try:
        db.setup()

    except peewee.OperationalError, e:
        sys.stderr.write('Error: %s\n' % e)
        sys.exit(1)

    except e:
        raise e
