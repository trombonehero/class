import banner.classlist
import humanize
import inflect
import requests
import sys


class_list = 'bwlkfcwl.P_FacClaListSum'
course_query = 'twgwlibs.P_CRNQueryResults'


def run(args, browser, db, urls):
    courses = []

    try:
        result = browser.get(urls.map(banner.classlist.class_list))
        if not result.ok: raise ValueError, result
        soup = result.soup

        (form,) = soup.findAll(lambda i: i.name == 'form' and
                                      i['action'].endswith('CRNQueryResults'))

        form.find('input', { 'name': 'p_term' })['value'] = args.term

        subject = form.find('select', { 'name': 'p_subj' })
        subject.find('option', { 'value': args.subject })['selected'] = True

        form.find('input', { 'name': 'p_crse' })['value'] = args.course_number

        result = browser.submit(form, urls.map(course_query))
        if not result.ok: raise ValueError, result

        tables = result.soup.findAll(lambda i: i.name == 'table' and
                                               'nowrap' in i.attrs)

        if len(tables) == 0:
            sys.stderr.write('No instances of %s %s found in term %s\n' % (
                args.subject, args.course_number, args.term))
            sys.stderr.write('Did you mean to use `--term 20xx0x`?\n')
            sys.exit(1)

        (table,) = tables
        rows = table.select('tr')
        headers = [ col.text for col in rows[1].select('th') ]

        for i in range(5, 8):
            headers[i] = headers[i] + ' Enrollment'

        for i in range(8, 11):
            headers[i] = headers[i] + ' Waitlist'

        for row in table.select('tr')[2:]:
            row = dict(zip(headers, ( col.text for col in row.select('td') )))
            courses.append(row)

    except requests.exceptions.ConnectionError, e:
        sys.stderr.write('Error: %s\n' % e.message)
        sys.exit(1)


    print('Found %s course %s:' % (
        humanize.apnumber(len(courses)),
        inflect.engine().plural('section', len(courses)),
    ))

    for course in courses:
        print('%6s %5s: %-20s   %3d/%3d registered (%3d remaining)' % (
            course['Term'], course['CRN'], course['Course'],
            int(course['Actual Enrollment']),
            int(course['Max Enrollment']),
            int(course['Remaining Enrollment']),
        ))
