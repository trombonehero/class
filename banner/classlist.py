import humanize
import inflect
import parse.classlist
import requests
import sys


class_list = 'bwlkfcwl.P_FacClaListSum'
set_crn = 'twgwlibs.P_CRNSelect'


def run(args, browser, db, urls):
    try:
        for crn in args.crn:
            print('Fetching classlist for CRN %s' % crn)

            browser.log.debug('Setting CRN %s: %s' % (crn, urls.map(set_crn)))
            result = browser.post(urls.map(set_crn), {
                'p_term': args.term,
                'p_crn': crn,
                'p_ret_loc': class_list,
            })
            if not result.ok: raise ValueError(result)

            browser.log.debug('Fetching class list: %s' % urls.map(class_list))
            result = browser.get(urls.map(class_list))
            if not result.ok: raise ValueError(result)

            (course_info, students) = parse.classlist.parse(result.soup)

            print(course_info['name'])
            print(course_info['duration'])
            print('%d students' % len(students))
            print('')

            (new, existing) = parse.classlist.save_students(students)
            print('%d existing students, %d new:' % (len(existing), len(new)))

            for s in new:
                print('%12s %9s %-24s' % (s.username, s.student_id, s.name()))

            print('')


    except requests.exceptions.ConnectionError as e:
        sys.stderr.write('Error: %s\n' % e.message)
        sys.exit(1)

    except ValueError as e:
        sys.stderr.write('Error: %s\n' % e)
        sys.exit(1)

