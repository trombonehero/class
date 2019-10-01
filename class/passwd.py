import click
import xkcdpass.xkcd_password as xkcd


@click.group('passwd')
@click.option('--length', default=4, show_default=True,
              help='number of words to use in each password')
@click.option('-n', '--no-save', is_flag=True, help="don't save anything")
@click.option('-w', '--wordfile', default=xkcd.locate_wordfile(),
              help='file containing source words')
@click.pass_context
def cli(ctx, length, no_save, wordfile):
    """Generate or reset user passwords."""

    ctx.ensure_object(dict)

    ctx.obj['length'] = length
    ctx.obj['save'] = not no_save
    ctx.obj['words'] = xkcd.generate_wordlist(wordfile)


@cli.command()
@click.argument('username', nargs=-1)
@click.option('--all-students', is_flag=True,
              help="initialize all currently-unset students' passwords")
@click.option('--filter', help='SQL filter for --all-students')
@click.pass_context
def init(ctx, username, all_students, filter):
    """Initialized unset passwords."""

    import itertools
    import passlib.apache
    import sys

    if len(username) == 0 and not all_students:
        sys.stderr.write('Must specify usernames or --all-students\n')
        sys.exit(1)

    from . import db

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
    cfg = ctx.obj

    for user in itertools.chain(instructors, students):
        password = xkcd.generate_xkcdpassword(cfg['words'], cfg['length'])
        htpasswd.set_password(user.username, password)

        filename = user.username + '.mail'
        print(f'Generating {filename}')
        f = open(filename, 'w')

        f.write('''
%s
Username:       %s
Password:       %s
Lab group(s):   %s
''' % (user, user.username, password,
       ', '.join([ str(g.group_id) for g in user.groups ])))

        if not cfg['save']:
            user.pw_hash = htpasswd.get_hash(user.username)
            user.save()

        f.close()


@cli.command()
@click.argument('username', nargs=-1)
@click.pass_context
def reset(ctx, username):
    """Reset passwords for specified usernames."""

    import itertools
    import passlib.apache

    from . import db

    usernames = username
    users = itertools.chain(
            db.Student.select().where(db.Student.username << usernames),
            db.Instructor.select().where(db.Instructor.username << usernames)
    )

    # Create a temporary, in-memory htpasswd "file" to hold generated passwords
    # in the proper Apache htpasswd format
    htpasswd = passlib.apache.HtpasswdFile()
    cfg = ctx.obj

    for user in users:
        password = xkcd.generate_xkcdpassword(cfg['words'], cfg['length'])
        htpasswd.set_password(user.username, password)

        print('%s: %s' % (user.username, password))

        if cfg['save']:
            user.pw_hash = htpasswd.get_hash(user.username)
            user.save()
