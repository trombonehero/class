import db
import errno
import json
import os


def setup_argparse(parser):
    parser.add_argument('-o', '--outdir', metavar = 'DIR', default = '.',
            help = 'directory to write SVN configuration files')

    parser.add_argument('-p', '--prefix', default = '',
            help = 'prefix for all directory paths (e.g., a year)')


def run(args, db):
    try: os.makedirs(args.outdir)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise

    groups = dict(
        (g.number, [ m.student.username for m in g.memberships ])
        for g in db.LabGroup.select()
    )

    students = db.Student.select()
    instructors = db.Instructor.select().where(db.Instructor.ta == False)
    tas = db.Instructor.select().where(db.Instructor.ta == True)


    print('Writing %d groups and %d students to authz' % (
        len(groups), len(students)))

    authz = open(os.path.join(args.outdir, 'authz'), 'w')

    authz.write('''
[groups]
instructors = {instructors}
tas = {tas}

[/]
@instructors = rw
@tas = r

[/TAs]
@tas = rw

'''.format(
        instructors = ','.join(i.username for i in instructors),
        tas = ','.join(t.username for t in tas))
    )

    for (number, members) in groups.items():
        path = os.path.join(args.prefix, 'groups', str(number))
        authz.write('[/%s]\n' % path)

        for m in members:
            authz.write('%s = rw\n' % m)

        authz.write('\n')

    for s in students:
        path = os.path.join(args.prefix, 'students', s.username)
        authz.write('[/%s]\n' % path)
        authz.write('%s = rw\n\n' % s.username)


    print('Writing %d groups to %s' % (len(groups), 'groups.json'))
    group_json = open(os.path.join(args.outdir, 'groups.json'), 'w')
    json.dump(groups, group_json)
