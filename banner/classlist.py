import humanize
import inflect
import parse.classlist
import requests
import sys


class_list = 'bwlkfcwl.P_FacClaListSum'
set_crn = 'twgwlibs.P_CRNSelect'


def run(args, browser, db, urls):
    try:
        result = browser.post(urls.map(set_crn), {
            'p_term': args.term,
            'p_crn': args.crn,
            'p_ret_loc': class_list,
        })
        if not result.ok: raise ValueError, result

        result = browser.get(urls.map(class_list))
        if not result.ok: raise ValueError, result

        (course_info, students) = parse.classlist.parse(result.soup)

        print(course_info['name'])
        print(course_info['duration'])
        print('%d students' % len(students))
        print('')

        (new, existing) = parse.classlist.save_students(students)
        print('%d new students, %d existing' % (new, existing))


    except requests.exceptions.ConnectionError, e:
        sys.stderr.write('Error: %s\n' % e.message)
        sys.exit(1)

    except ValueError, e:
        sys.stderr.write('Error: %s\n' % e)
        sys.exit(1)

