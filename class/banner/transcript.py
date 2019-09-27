import banner
import datetime
import parse.transcript
import peewee
import requests
import sys


display_transcript = 'bwlkftrn.P_FacDispTran'
store_id = 'bwlkoids.P_AdvStoreID'
verify_id = 'bwlkoids.P_AdvVerifyID'
view_transcript = 'bwlkftrn.P_ViewTran'


def run(args, browser, db, urls):
    if bool(args.all) == bool(args.id):   # Python has no xor (!?)
        sys.stderr.write('Error: need exactly one of --all or student_id\n')
        sys.exit(1)

    term = args.term

    if args.id:
        formatted_id = '{0:09d}'.format(int(args.id))
        (name, courses) = fetch_transcript(browser, urls, term, formatted_id)

        print('Retrieved transcript for %s' % name)
        print('')
        parse.transcript.print_courses(courses)

        try:
            student = db.Student.get(student_id=formatted_id)
            save(db, student, courses)

        except peewee.DoesNotExist:
            sys.stderr.write('\n%s (%s) not a student in this database\n' % (
                name, args.id))
            sys.exit(1)

    else:
        students = (
            db.Student.select()
                      .where(db.Student.transcript_fetched == None)
        )

        print('Retrieving %d transcripts:' % students.count())

        for s in students:
            sys.stdout.write('%9s %-30s  ' % (s.student_id, s.name))

            formatted_id = '{0:09d}'.format(s.student_id)
            (_, courses) = fetch_transcript(browser, urls, term, formatted_id)
            if courses is None:
                sys.stdout.write('ERROR\n')
                continue

            save(db, s, courses)

            sys.stdout.write('%3d courses\n' % len(courses))


def fetch_transcript(browser, urls, term, student_id):
    browser.log.info('Fetching transcript for %s' % student_id)
    try:
        browser.log.debug('Requesting %s' % urls.map(verify_id))
        result = browser.post(urls.map(verify_id), {
            'TERM': term,
            'STUD_ID': student_id,
        })
        if not result.ok:
            raise ValueError(result)

        #
        # The form that Banner returns here contains a challenge nonce,
        # so we need to use the form rather than go directly to the transcript.
        #
        forms = result.soup.findAll(lambda tag: tag.name == 'form' and
                                    tag['action'].endswith(store_id))

        if len(forms) == 0:
            sys.stderr.write(
                'no verification form found for %s\n' % student_id)
            return (None, None)

        (form,) = forms
        form.input({'sname': store_id})

        browser.log.debug('Requesting transcript: %s' % urls.map(verify_id))
        result = browser.submit(form, urls.map(display_transcript))
        if not result.ok:
            raise ValueError(result)

        browser.log.debug('Displaying transcript: %s' % urls.map(verify_id))
        result = browser.get(urls.map(display_transcript))
        if not result.ok:
            raise ValueError(result)

        browser.log.debug('"Viewing" transcript: %s' % urls.map(verify_id))
        result = browser.post(urls.map(view_transcript), {
            'tprt': 'OFFR',     # show transcript as of today
        })
        if not result.ok:
            raise ValueError(result)

        try:
            return parse.transcript.parse(result.soup)
        except ValueError as e:
            exc_info = sys.exc_info()
            msg = str(e)
            raise banner.ParseError(msg, result.soup, exc_info)

    except requests.exceptions.ConnectionError as e:
        sys.stderr.write('Error: %s\n' % e.message)
        sys.exit(1)


def save(db, student, courses):
    assert student is not None

    for course in courses:
        ((year, term), subject, code, title, grade) = course

        e, created = db.TranscriptEntry.get_or_create(
            student=student, year=year, term=term,
            subject=subject, code=code,
            defaults={'result': grade})

        try:
            e.mark = int(grade)
        except ValueError:
            pass

        e.save()

    student.transcript_fetched = datetime.datetime.now()
    student.save()
