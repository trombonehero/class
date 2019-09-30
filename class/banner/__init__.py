import getpass
import importlib
import logging
import mechanicalsoup
import os
import requests
import sys
import traceback

from .. import config


class LoginError(BaseException):
    def __init__(self, username='<unknown>', cause=None):
        """
        username: the Banner username we tried to log in with
        cause: a (type,value,traceback) triple from sys.exc_info()
        """

        self.username = username
        self.cause = cause

    def __str__(self):
        if self.cause:
            traceback.print_exception(*self.cause)

        return 'LoginError: failed to log in as %s' % self.username


class ParseError(BaseException):
    def __init__(self, message, soup, cause=None):
        """
        message: a user-readable string
        soup: the BeautifulSoup object for the complete web page
        cause: a (type,value,traceback) triple from sys.exc_info()
        """

        import codecs
        import tempfile

        self.message = message
        self.soup = soup
        self.cause = cause

        self.filename = tempfile.NamedTemporaryFile().name
        self.file = codecs.open(self.filename, 'w', 'utf-8')

        self.file.write(soup.prettify())

    def __str__(self):
        if self.cause:
            traceback.print_exception(*self.cause)

        return 'ParseError: %s (see contents of %s)' % (
            self.message, self.filename)


def setup_argparse(parser):
    parser.add_argument('--banner-root', default=config.banner_root,
                        help='Root URL for all Banner requests')
    parser.add_argument('--ca-bundle', default=False,
                        help='path to CA certificate bundle')
    parser.add_argument('--credential-file', default=config.credential_file,
                        help='username/password file (YAML format)')
    parser.add_argument('--term', default=config.term,
                        help='e.g., Fall 2016: 201601 [default: %s]' %
                        config.term)

    subparsers = parser.add_subparsers(dest='banner_command')

    crn = subparsers.add_parser('crn', help='find course CRN from Banner')
    crn.add_argument('subject', help='academic subject (e.g., ENGI)')
    crn.add_argument('course_number', help='course number (e.g., 3891)')

    classlist = subparsers.add_parser('classlist', help='fetch class list')
    classlist.add_argument('crn', help='Course Registration Number',
                           nargs='+')

    transcript = subparsers.add_parser('transcript', help='fetch transcript')
    transcript.add_argument('--all', '-a', action='store_true',
                            help="fetch entire class' transcripts")
    transcript.add_argument('id', nargs='?',
                            help="fetch only this student's transcript")


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
        print("No '%s', prompting for user input" % args.credential_file)
        credential = {
            'username': input('Username: '),
            'password': getpass.getpass(),
        }

    try:
        browser = login(credential, urls, args.ca_bundle)
        browser.set_term(args.term, urls)

    except requests.exceptions.ConnectionError as e:
        sys.stderr.write('Error: %s\n' % e)
        return

    except ValueError as e:
        sys.stderr.write('Error: %s\n' % e)
        return

    command = 'banner.' + args.banner_command
    importlib.import_module(command).run(args, browser, db, urls)


def login(credential, urls, ca_bundle):
    login_prompt = 'twbkwbis.P_WWWLogin'
    login_verify = 'twbkwbis.P_ValLogin'

    browser = mechanicalsoup.Browser(soup_config={'features': 'html.parser'})
    browser.log = logging.getLogger()

    browser.log.info('Logging in via %s' % urls.map(login_prompt))
    browser.get(urls.map(login_prompt), verify=ca_bundle)
    result = browser.post(urls.map(login_verify), {
        'sid': credential['username'],
        'PIN': credential['password'],
    })

    if not result.ok:
        raise ValueError(result)

    import types
    browser.ca_bundle = ca_bundle
    browser.set_term = types.MethodType(set_term, browser)
    browser.urls = urls

    return browser


def set_term(browser, term, urls):
    """
    Set the term (e.g., Fall 2016) on the current browser session.

    Unfortunately, Banner doesn't accept explicit term arguments, but instead
    stores this information in server-side session state. To make it easier to
    deal with this design decision, this function manipulates a Mechanical Soup
    browser object to send a form response to Banner with the session's term ID.
    """

    term_set = 'bwlkostm.P_FacStoreTerm2'

    browser.log.debug('Setting term to %s @ %s' % (term, urls.map(term_set)))
    result = browser.post(browser.urls.map(term_set), {'term': term})

    if not result.ok:
        raise ValueError(result)

    return result