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
            help = 'file containing source words',
            default = xkcd.locate_wordfile())

    parser.add_argument('username', nargs = '*',
            help = 'users to create passwords for')


def run(args, db):
    if (len(args.username) == 0) != args.all_students:
        sys.stderr.write('Must specify usernames or --all-students\n')
        sys.exit(1)

    words = xkcd.generate_wordlist(args.wordfile)
    students = db.Student.select().where(db.Student.pw_hash == None)

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

        matches = [u.username for u in itertools.chain(instructors, students)]
        unmatched = set(usernames).difference(matches)
        if len(unmatched) > 0:
            sys.stderr.write(f'Invalid usernames: {" ".join(unmatched)}\n')

    if args.filter:
        students = students.where(db.SQL(args.filter))

    # Create a temporary, in-memory htpasswd "file" to hold generated passwords
    # in the proper Apache htpasswd format
    htpasswd = passlib.apache.HtpasswdFile()

    for user in itertools.chain(instructors, students):
        password = xkcd.generate_xkcdpassword(words, int(args.length))
        htpasswd.set_password(user.username, password)

        f = open(user.username + '.mail', 'w')

        f.write('''
%s
Username:       %s
Password:       %s
Lab group(s):   %s
''' % (user, user.username, password,
       ', '.join([ str(g.group_id) for g in user.groups ])))

        if not args.no_save:
            user.pw_hash = htpasswd.get_hash(user.username)
            user.save()

        f.close()
