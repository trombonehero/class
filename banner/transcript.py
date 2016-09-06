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
        (name, courses) = fetch_transcript(browser, urls, term, args.id)

        print('Retrieved transcript for %s' % name)
        print('')
        parse.transcript.print_courses(courses)

        try:
            student = db.Student.get(student_id = args.id)
            save(db, student, courses)

        except peewee.DoesNotExist:
            sys.stderr.write('\n%s (%s) not a student in this database\n' % (
                name, args.id))
            sys.exit(1)


    else:
        students = (
            db.Student.select()
                      .join(db.TranscriptEntry, peewee.JOIN.LEFT_OUTER)
                      .where(db.TranscriptEntry.student == None)
        )

        print('Retrieving %d transcripts:' % students.count())

        for s in students:
            sys.stdout.write('%9s %-30s  ' % (s.student_id, s.name()))

            (_, courses) = fetch_transcript(browser, urls, term, s.student_id)
            if courses is None:
                sys.stdout.write('ERROR\n')
                continue

            save(db, s, courses)

            sys.stdout.write('%3d courses\n' % len(courses))


def fetch_transcript(browser, urls, term, student_id):
    try:
        result = browser.post(urls.map(verify_id), {
            'TERM': term,
            'STUD_ID': student_id,
        })
        if not result.ok: raise ValueError, result

        #
        # The form that Banner returns here contains a challenge nonce,
        # so we need to use the form rather than go directly to the transcript.
        #
        forms = result.soup.findAll(lambda tag: tag.name == 'form' and
                                    tag['action'].endswith(store_id))

        if len(forms) == 0:
            sys.stderr.write('no verification form found for %s\n' % student_id)
            return (None, None)

        (form,) = forms
        form.input({ 'sname': store_id })

        result = browser.submit(form, urls.map(display_transcript))
        if not result.ok: raise ValueError, result

        result = browser.get(urls.map(display_transcript))
        if not result.ok: raise ValueError, result

        result = browser.post(urls.map(view_transcript), {
            'tprt': 'OFFR',     # show transcript as of today
        })
        if not result.ok: raise ValueError, result

        return parse.transcript.parse(result.soup)


    except requests.exceptions.ConnectionError, e:
        sys.stderr.write('Error: %s\n' % e.message)
        sys.exit(1)

    except ValueError, e:
        sys.stderr.write('Error: %s\n' % e)
        sys.exit(1)


def save(db, student, courses):
    assert student is not None

    for course in courses:
        ((year, term), subject, code, title, grade) = course

        e, created = db.TranscriptEntry.get_or_create(
                student = student, year = year, term = term,
                subject = subject, code = code,
                defaults = { 'result': grade })

        try: e.mark = int(grade)
        except ValueError: pass

        e.save()
