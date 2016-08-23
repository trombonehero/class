from bs4 import BeautifulSoup
import collections
from db import Student

def run(args, db):
    course_info = None
    student_details = []

    for filename in args.file:
        soup = BeautifulSoup(open(filename, 'r'), "html.parser")
        (info, students) = parse(soup)

        if not course_info: course_info = info
        assert course_info == info

        student_details += students

    course_info = { k.strip(): v for (k,v) in course_info.items() }

    print('%s (CRN %d)' % (course_info['name'], course_info['crn']))
    print(course_info['duration'])
    print('')

    (new, existing) = save_students(student_details)
    print('%d new students, %d existing' % (new, existings))


def save_students(students):
    new = 0

    for sd in students:
        username = sd['email'].split('@')[0]

        existing = Student.select().where(Student.student_id == sd['id'])
        new_student = (existing.count() == 0)

        s = Student(student_id = sd['id']) if new_student else existing.get()

        s.username = username
        (s.surname, s.forename) = sd['name'].split(', ')
        s.graduate_student = sd['degree'].startswith('Graduate')

        if s.forename.endswith('.'):
            forenames = s.forename.split()
            s.forename = ' '.join(forenames[:-1])
            s.initial = forenames[-1][:-1]

        # Since Student has a custom primary key (the student ID), we need 
        # to force the use of INSERT on our first call to save()
        s.save(force_insert = new_student)

        new += new_student

    return (new, len(students) - new)


def parse(soup):
    """
    Parse the HTML output of Banner's "Summary Class List", returning
    a tuple with a dictionary of class information (class name, etc.)
    and a list of student dictionaries.

    Example usage:
    (course_info, students) = banner.classlist.parse_html(open(filename, 'r'))

    print('%s (CRN %d)' % (course_info['name'], course_info['crn']))
    print(course_info['duration'])
    print('')

    for s in sorted(students, key = lambda s: s.name):
        print('%9d %14s %-40s' % (s['id'], s['email'], s['name']))
    """

    raw_tables = soup.findAll('table', **{ 'class': 'datadisplaytable' })
    tables = dict([ (t.caption.text, t) for t in raw_tables ])

    course_info = tables['Course Information'].findAll('tr')
    course_info = dict(
        zip([ 'name', 'crn', 'duration', 'status' ],
            [ i.text.strip() for i in course_info ])
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
            k: converters[k](v) for (k,v) in 
            zip(
                [ 'name', 'id', 'status', 'degree', 'credit_hours', 'grade', 'email' ],
                columns[1:]
            )
        }

        students.append(columns)

    return (course_info, students)
