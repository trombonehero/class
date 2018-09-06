import itertools
import passlib.apache
import requests
import sys
import xkcdpass.xkcd_password as xkcd


def setup_argparse(parser):
    parser.add_argument('--length', default = 4,
            help = 'number of words to use in each password')

    parser.add_argument('-n', '--no-save', action = 'store_true',
            help = "don't save: test password initialization")

    parser.add_argument('-w', '--wordfile',
            help = 'file containing source words',
            default = xkcd.locate_wordfile())

    parser.add_argument('username', nargs = '+',
            help = 'users to reset passwords for')


def run(args, db):
    usernames = args.username
    users = itertools.chain(
            db.Student.select().where(db.Student.username << usernames),
            db.Instructor.select().where(db.Instructor.username << usernames)
    )

    # Create a temporary, in-memory htpasswd "file" to hold generated passwords
    # in the proper Apache htpasswd format
    htpasswd = passlib.apache.HtpasswdFile()

    words = xkcd.generate_wordlist(args.wordfile)
    for user in users:
        password = xkcd.generate_xkcdpassword(words, int(args.length))
        htpasswd.set_password(user.username, password)

        print('%s: %s' % (user.username, password))

        if not args.no_save:
            user.pw_hash = htpasswd.get_hash(user.username)
            user.save()
