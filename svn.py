import db
import errno
import itertools
import json
import os


def setup_argparse(parser):
    parser.add_argument('-o', '--outdir', metavar = 'DIR', default = '.',
            help = 'directory to write SVN configuration files')

    parser.add_argument('-r', '--repo', required = True,
            help = 'repository name (e.g., engi4892)')

    parser.add_argument('-p', '--prefix', default = '',
            help = 'prefix for SVN paths in the repo (e.g., 2018-19W)')


def run(args, db):
    try: os.makedirs(args.outdir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    groups = dict(
        (g.number, [ m.student.username for m in g.memberships ])
        for g in db.LabGroup.select()
    )
    groups[0] = [ '@instructors', '@tas' ]

    students = list(db.Student.select())
    instructors = list(db.Instructor.select().where(db.Instructor.ta == False))
    tas = list(db.Instructor.select().where(db.Instructor.ta == True))

    print('Writing %d groups and %d students to authz' % (
        len(groups), len(students)))

    authz = open(os.path.join(args.outdir, 'authz'), 'w')

    authz.write('''
[groups]
instructors = {instructors}
tas = {tas}

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

'''.format(
        instructors = ','.join(i.username for i in instructors),
        prefix = args.prefix,
        repo = args.repo,
        tas = ','.join(t.username for t in tas),
    ))

    for (number, members) in groups.items():
        path = os.path.join(args.prefix, 'groups', str(number))
        authz.write('[%s:/%s]\n' % (args.repo, path))

        for m in members:
            authz.write('%s = rw\n' % m)

        authz.write('\n')

    for s in students:
        path = os.path.join(args.prefix, 'students', s.username)
        authz.write('[%s:/%s]\n' % (args.repo, path))
        authz.write('%s = rw\n\n' % s.username)


    print('Writing %d instructors, %d TAs and %d students to %s' % (
        len(instructors), len(tas), len(students), 'htpasswd'))

    htpasswd = open(os.path.join(args.outdir, 'htpasswd'), 'w')

    for user in itertools.chain(instructors, tas, students):
        if user.pw_hash:
            htpasswd.write('%s:%s\n' % (user.username, user.pw_hash))


    print('Writing %d groups to %s' % (len(groups), 'groups.json'))
    group_json = open(os.path.join(args.outdir, 'groups.json'), 'w')
    json.dump(groups, group_json)
