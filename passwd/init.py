import itertools
import passlib.apache
import requests
import sys
import xkcdpass.xkcd_password as xkcd


def setup_argparse(parser):
    parser.add_argument('--all-students', action = 'store_true',
            help = "initialize all currently-unset students' passwords")

    parser.add_argument('--filter', help = 'SQL filter for --all-students')

    parser.add_argument('--length', default = 4,
            help = 'number of words to use in each password')

    parser.add_argument('-n', '--no-save', action = 'store_true',
            help = "don't save: test password initialization")

    parser.add_argument('-w', '--wordfile',
            help = 'file containing source words')

    parser.add_argument('username', nargs = '*',
            help = 'users to create passwords for')


def run(args, db):
    if (len(args.username) == 0) != args.all_students:
        sys.stderr.write('Must specify usernames or --all-students\n')
        sys.exit(1)

    if args.wordfile:
        words = xkcd.generate_wordlist(args.wordfile)
    else:
        words = xkcd.locate_wordfile()

    students = (
            db.Student.select()
                      .where(db.Student.pw_hash == None)
                      .join(db.GroupMembership)
                      .group_by(db.GroupMembership.student)
                      .order_by(db.GroupMembership.group)
    )

    if args.all_students:
        instructors = []

    else:
        usernames = args.username

        students = students.where(db.Student.username << usernames)
        instructors = (
                db.Instructor.select()
                             .where(db.Instructor.pw_hash == None)
                             .where(db.Instructor.username << usernames)
        )

    if args.filter:
        students = students.where(db.SQL(args.filter))

    # Create a temporary, in-memory htpasswd "file" to hold generated passwords
    # in the proper Apache htpasswd format
    htpasswd = passlib.apache.HtpasswdFile()

    for user in itertools.chain(instructors, students):
        password = xkcd.generate_xkcdpassword(words, int(args.length))
        htpasswd.set_password(user.username, password)

        print(user.name())
        print('Username:      %s' % user.username)
        print('Password:      %s' % password)
        print('Lab group(s):  %s' % ', '.join([
            str(g.group_id) for g in user.groups ]))
        print('')

        if not args.no_save:
            user.pw_hash = htpasswd.get_hash(user.username)
            user.save()
