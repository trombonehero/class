import click
import os


@click.command('svn')
@click.option('-o', '--outdir', metavar='DIR', default='.', show_default=True,
              help='Directory to write SVN configuration files into')
@click.option('-r', '--repo', required=True,
              help='Repository name (e.g., engi4892)')
@click.option('-p', '--prefix', default='',
              help='prefix for SVN paths in the repo (e.g., "2018-19W")')
@click.pass_context
def cli(ctx, outdir, repo, prefix):
    """Generate Subversion repository configuration directory."""

    try: os.makedirs(outdir)
    except OSError as e:
        import errno
        if e.errno != errno.EEXIST:
            raise

    from . import db

    # Find all lab groups; set "group 0" to be the instructor and TAs
    groups = dict(
        (g.number, [ m.student.username for m in g.memberships ])
        for g in db.LabGroup.select()
    )
    groups[0] = [ '@instructors', '@tas' ]

    students = list(db.Student.select())
    instructors = list(db.Instructor.select().where(db.Instructor.ta == False))
    tas = list(db.Instructor.select().where(db.Instructor.ta == True))

    with open(os.path.join(outdir, 'authz'), 'w') as authz:
        write_authz(authz, groups, instructors, tas, students, repo, prefix)

    with open(os.path.join(outdir, 'htpasswd'), 'w') as htpasswd:
        write_htpasswd(htpasswd, instructors, tas, students)

    with open(os.path.join(outdir, 'groups.json'), 'w') as group_json:
        write_groups(group_json, groups)


def write_authz(f, groups, instructors, tas, students, repo, prefix):
    print(f'Writing {len(groups)} groups, {len(students)} students to {f.name}')

    f.write(f'''
[groups]
instructors = {','.join(i.username for i in instructors)}
tas = {','.join(t.username for t in tas)}

[{repo}:/]
@instructors = rw

[{repo}:/{prefix}]
@instructors = rw
@tas = r

[{repo}:/{prefix}/common]
* = r
@instructors = rw
@tas = rw

[{repo}:/{prefix}/TAs]
@tas = rw

''')

    for (number, members) in groups.items():
        path = os.path.join(prefix, 'groups', str(number))
        f.write(f'[{repo}:/{path}]\n')

        for m in members:
            f.write(f'{m} = rw\n')

        f.write('\n')

    for s in students:
        f.write(f'[{repo}:/{prefix}/students/{s.username}]\n')
        f.write(f'{s.username} = rw\n\n')


def write_htpasswd(htpasswd, instructors, tas, students):
    import itertools

    print(f'Writing {len(instructors)} instructors, {len(tas)} TAs and ' +
        f'{len(students)} students to {htpasswd.name}')

    for user in itertools.chain(instructors, tas, students):
        if user.pw_hash:
            htpasswd.write('%s:%s\n' % (user.username, user.pw_hash))


def write_groups(group_json, groups):
    import json

    print(f'Writing {len(groups)} groups to {group_json.name}')
    json.dump(groups, group_json)
