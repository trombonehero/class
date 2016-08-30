import parse.transcript
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

    if args.id:
        (name, courses) = fetch_transcript(browser, urls, args.term, args.id)

        print('Retrieved transcript for %s' % name)
        print('')
        parse.transcript.print_courses(courses)

    else:
        sys.stderr.write('Multi-transcript retrieval not yet supported\n')
        sys.exit(1)


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
        (form,) = result.soup.findAll(lambda tag: tag.name == 'form' and
                                      tag['action'].endswith(store_id))

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

