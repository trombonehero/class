import config
import getpass
import importlib
import mechanicalsoup
import os
import requests
import sys


def setup_argparse(parser):
    parser.add_argument('--banner-root', default = config.banner_root,
            help = 'Root URL for all Banner requests')
    parser.add_argument('--ca-bundle', default = False,
            help = 'path to CA certificate bundle')
    parser.add_argument('--credential-file', default = config.credential_file,
            help = 'username/password file (YAML format)')
    parser.add_argument('--term', default = config.term,
            help = 'e.g., Fall 2016: 201601 [default: %s]' % config.term)

    subparsers = parser.add_subparsers(dest = 'banner_command')

    crn = subparsers.add_parser('crn', help = 'find course CRN from Banner')
    crn.add_argument('subject', help = 'academic subject (e.g., ENGI)')
    crn.add_argument('course_number', help = 'course number (e.g., 3891)')

    classlist = subparsers.add_parser('classlist', help = 'fetch class list')
    classlist.add_argument('crn', help = 'Course Registration Number')

    transcript = subparsers.add_parser('transcript', help = 'fetch transcript')
    transcript.add_argument('--all', '-a', action = 'store_true',
            help = "fetch entire class' transcripts")
    transcript.add_argument('id', nargs = '?',
            help = "individual student's ID (fetch only one transcript)")


class urlmapper:
    def __init__(self, root):
        self.root = root

    def map(self, relative):
        return '%s/%s' % (self.root, relative)


def run(args, db):
    urls = urlmapper(args.banner_root)

    if os.path.isfile(args.credential_file):
        import yaml
        credential = yaml.load(open(args.credential_file))

    else:
        credential = {
            'username': raw_input('Username: '),
            'password': getpass.getpass(),
        }

    try:
        browser = login(credential, urls, args.ca_bundle)
        browser.set_term(args.term)

    except requests.exceptions.ConnectionError, e:
        sys.stderr.write('Error: %s\n' % e.message)
        return

    except ValueError, e:
        sys.stderr.write('Error: %s\n' % e)
        return


    command = 'banner.' + args.banner_command
    importlib.import_module(command).run(args, browser, db, urls)


def login(credential, urls, ca_bundle):
    login_prompt = 'twbkwbis.P_WWWLogin'
    login_verify = 'twbkwbis.P_ValLogin'

    browser = mechanicalsoup.Browser(soup_config={'features': 'html.parser'})

    browser.get(urls.map(login_prompt), verify = ca_bundle)
    result = browser.post(urls.map(login_verify), {
        'sid': credential['username'],
        'PIN': credential['password'],
    })

    if not result.ok: raise ValueError, result

    import types
    browser.ca_bundle = ca_bundle
    browser.set_term = types.MethodType(set_term, browser)
    browser.urls = urls

    return browser


def set_term(browser, term):
    """
    Set the term (e.g., Fall 2016) on the current browser session.

    Unfortunately, Banner doesn't accept explicit term arguments, but instead
    stores this information in server-side session state. To make it easier to
    deal with this design decision, this function manipulates a Mechanical Soup
    browser object to send a form response to Banner with the session's term ID.
    """

    term_set = 'bwlkostm.P_FacStoreTerm2'

    result = browser.post(browser.urls.map(term_set), { 'term': term })

    if not result.ok: raise ValueError, result

    return result
