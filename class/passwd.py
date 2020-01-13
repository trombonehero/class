import click
import xkcdpass.xkcd_password as xkcd

length = 4
save = True
wordlist = None


@click.group('passwd')
@click.option('--words', default=4, show_default=True,
              help='number of words to use in each password')
@click.option('-n', '--no-save', is_flag=True, help="don't save anything")
@click.option('--wordfile', default=xkcd.locate_wordfile(),
              help='file containing source words')
def cli(words, no_save, wordfile):
    """Generate or reset user passwords."""

    global length, save, wordlist

    length = int(words)
    save = not no_save
    wordlist = xkcd.generate_wordlist(wordfile)


@cli.command()
@click.argument('username', nargs=-1)
@click.option('--all-students', is_flag=True,
              help="initialize all currently-unset students' passwords")
@click.option('--filter', help='SQL filter for --all-students')
@click.pass_obj
def init(db, username, all_students, filter):
    """Initialized unset passwords."""

    import itertools
    import passlib.apache
    import sys

    if len(username) == 0 and not all_students:
        sys.stderr.write('Must specify usernames or --all-students\n')
        sys.exit(1)

    students = db.Student.select().where(db.Student.pw_hash == None)

    if all_students:
        instructors = []

    else:
        usernames = username

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

    if filter:
        students = students.where(db.SQL(filter))

    # Create a temporary, in-memory htpasswd "file" to hold generated passwords
    # in the proper Apache htpasswd format
    htpasswd = passlib.apache.HtpasswdFile()

    for user in itertools.chain(instructors, students):
        password = xkcd.generate_xkcdpassword(wordlist, length)
        htpasswd.set_password(user.username, password)

        filename = user.username + '.mail'
        print(f'Generating {filename}')
        f = open(filename, 'w')

        f.write(f'''
{user}
Username:       {user.username}
Password:       {password}
Lab group(s):   {', '.join([str(g.group_id) for g in user.groups])}
''')

        if not save:
            user.pw_hash = htpasswd.get_hash(user.username)
            user.save()

        f.close()


@cli.command()
@click.argument('username', nargs=-1)
@click.pass_obj
def reset(db, username):
    """Reset passwords for specified usernames."""

    import itertools
    import passlib.apache

    usernames = username
    users = itertools.chain(
        db.Student.select().where(db.Student.username << usernames),
        db.Instructor.select().where(db.Instructor.username << usernames),
    )

    # Create a temporary, in-memory htpasswd "file" to hold generated passwords
    # in the proper Apache htpasswd format
    htpasswd = passlib.apache.HtpasswdFile()

    for user in users:
        password = xkcd.generate_xkcdpassword(wordlist, length)
        htpasswd.set_password(user.username, password)

        print('%s: %s' % (user.username, password))

        if save:
            user.pw_hash = htpasswd.get_hash(user.username)
            user.save()
