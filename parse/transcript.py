from bs4 import BeautifulSoup
import collections


def run(args, db):
    soup = BeautifulSoup(open(args.file, 'r'), "html.parser")
    (name, courses) = parse(soup)

    print('Parsed transcript for %s:' % name)
    print('')
    print_courses(courses)


def print_courses(courses):
    marks = collections.defaultdict(list)
    grades = collections.defaultdict(int)

    for ((year, term), subject, course, title, mark) in courses:
        print('%4s %4s  %-32s %s' % (subject, course, title, mark))

        try:
            mark = float(mark)

            marks[subject].append(mark)
            marks['*'].append(mark)

            grades[grade(mark)] += 1


        except ValueError:
            pass

    print('')
    for g in 'ABCDF':
        print('  %c   %2d  %s' % (g, grades[g], '*' * grades[g]))

    print('')
    print('  Subj   N   Min   Avg   Max')
    print('  ----  --   ---  -----  ---')
    for subject in sorted(marks.keys(), key = lambda k: len(marks[k]),
                          reverse = True):

        sub_marks = marks[subject]
        print('  %4s  %2d   %2d%%  %0.1f%%  %2d%%' % (
            subject, len(sub_marks),
            min(sub_marks),
            sum(sub_marks) / float(len(sub_marks)),
            max(sub_marks),
        ))


def grade(mark):
    if mark >= 80: return 'A'
    if mark >= 65: return 'B'
    if mark >= 55: return 'C'
    if mark >= 50: return 'D'
    return 'F'


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

    (table,) = soup.findAll('table', **{ 'class': 'datadisplaytable' })

    name = None
    courses = []

    in_grades_section = False
    headers = None
    term = None

    for row in table.select('tr'):
        th = row.select('th')

        if in_grades_section:
            if len(th) > 1:
                if headers is None and th[0].text == 'Subject':
                    headers = [ i.text for i in th ]

            if len(th) > 0:
                thtext = th[0].text

                if thtext.startswith('Term: '):
                    (year, season) = thtext[5:].split()

                    year = int(year[:4])
                    season = {
                        'Fall': 1,
                        'Winter': 2,
                        'Spring': 3,
                    }[season]

                    term = (year, season)

            else:
                columns = row.findAll('td')

                if headers is None:
                    # This row probably describes transfer credit,
                    # which is not a normal transcript entry for our purposes.
                    continue

                if len(columns) == len(headers) + 1:        # don't ask.
                    detail = dict(
                        zip(headers, [ c.text for c in row.findAll('td') ])
                    )

                    course = (
                        term,
                        detail['Subject'],
                        detail['Course'].strip(),
                        detail['Title'].strip(),
                        detail['Grade'].strip(),
                    )

                    courses.append(course)

        else:
            if len(th) == 0:
                continue

            if th[0].text == 'Name :':
                assert name is None
                name = row.td.text

            if th[0].text.startswith('INSTITUTION CREDIT'):
                in_grades_section = True

    return (name, courses)
