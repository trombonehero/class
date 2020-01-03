import click


@click.group('classlist')
def cli():
    """Parse a classlist/roster."""
    pass


@cli.command()
@click.argument('html', type=click.File(), nargs=-1, required=True)
@click.pass_obj
def banner(db, html):
    """Parse a Banner class list."""

    from bs4 import BeautifulSoup

    course_info = None
    student_details = []

    for html_file in html:
        soup = BeautifulSoup(html_file, "html.parser")
        info, students = parse(soup)

        if not course_info:
            course_info = info
        elif course_info != info:
            raise ValueError(f'course mismatch: {info} vs {course_info}')

        student_details += students

    course_info = {k.strip(): v for (k, v) in course_info.items()}

    print('%s (CRN %d)' % (course_info['name'], course_info['crn']))
    print(course_info['duration'])
    print('')

    (new, existing) = save_students(db, student_details)
    print('%d existing students, %d new:' % (len(existing), len(new)))

    for s in new:
        print('%12s %9s %-24s' % (s.username, s.student_id, s.name()))


@cli.command()
@click.argument('csv_file', type=click.File())
@click.pass_obj
def gradescope(db, csv_file):
    """Parse a Gradescope roster (CSV format)."""

    import csv

    # Read CSV headers from the first row
    r = csv.reader(csv_file)
    headers = next(r)

    # Parse student details
    students = []
    for row in r:
        data = dict(zip(headers, row))

        if data['Role'] != 'Student':
            print(f"{data['SID']}/{data['SID']} not a student ({data['Role']})")
            continue

        # Translate from Gradescope roster to expected format
        students.append({
            'name': data['Name'],
            'id': data['SID'],
            'email': data['Email'],
            'degree': data['Role'],
        })

    (new, existing) = save_students(db, students)
    print('%d existing students, %d new:' % (len(existing), len(new)))

    for s in new:
        print('%12s %9s %-24s' % (s.username, s.student_id, s.name()))


def save_students(db, students):
    (new_students, existing_students) = ([], [])

    for sd in students:
        username = sd['email'].split('@')[0]

        existing = db.Student.select().where(db.Student.student_id == sd['id'])
        new_student = (existing.count() == 0)

        s = db.Student(student_id=sd['id']) if new_student else existing.get()

        s.username = username
        s.graduate_student = sd['degree'].startswith('Graduate')

        if ', ' in sd['name']:
            (s.surname, s.forename) = sd['name'].split(', ')
        else:
            (s.surname, s.forename) = sd['name'].rsplit(' ', 1)

        if s.forename.endswith('.'):
            forenames = s.forename.split()
            s.forename = ' '.join(forenames[:-1])
            s.initial = forenames[-1][:-1]

        # Since Student has a custom primary key (the student ID), we need
        # to force the use of INSERT on our first call to save()
        s.save(force_insert=new_student)

        (new_students if new_student else existing_students).append(s)

    return (new_students, existing_students)


def parse_banner(soup):
    """
    Parse the HTML output of Banner's "Summary Class List", returning
    a tuple with a dictionary of class information (class name, etc.)
    and a list of student dictionaries.

    Example usage:
    (course_info, students) = classlist.parse_banner(open(filename, 'r'))

    print('%s (CRN %d)' % (course_info['name'], course_info['crn']))
    print(course_info['duration'])
    print('')

    for s in sorted(students, key = lambda s: s.name):
        print('%9d %14s %-40s' % (s['id'], s['email'], s['name']))
    """

    import collections

    raw_tables = soup.findAll('table', **{'class': 'datadisplaytable'})
    tables = dict([(t.caption.text, t) for t in raw_tables])

    course_info = tables['Course Information'].findAll('tr')
    course_info = dict(
        zip(['name', 'crn', 'duration', 'status'],
            [i.text.strip() for i in course_info])
    )

    # Return "Duration:\n" prefix from duration string
    course_info['duration'] = ' '.join(course_info['duration'].split()[1:])

    course_info['crn'] = int(course_info['crn'].split(':')[1])

    students = []
    converters = collections.defaultdict(lambda: lambda c: c.text.strip())
    converters['id'] = lambda c: int(c.text)
    converters['email'] = lambda c: c.find('a')['href'].split(':')[1]

    for row in tables['Summary Class List'].findAll('tr'):
        columns = row.findAll('td')
        if len(columns) == 1:
            continue

        columns = {
            k: converters[k](v) for (k, v) in
            list(zip(
                ['name', 'id', 'status', 'degree',
                    'credit_hours', 'grade', 'email'],
                columns[1:]
            ))
        }

        students.append(columns)

    return (course_info, students)
