import click
import datetime


#
# In Banner, terms are numbered as:
#
# 20xx01: Fall 20xx (Sep-Dec 20xx)
# 20xx02: Winter 20xx (Jan-Apr 20xx+1)
# 20xx03: Spring 20xx (May-Aug 20xx+1)
#
today = datetime.date.today()
term = ((today.month - 9) % 12) / 4 + 1
term = '%04d%02d' % (today.year - term / 2, term)

browser = None


class urlmapper:
    def __init__(self, root):
        self.root = root

    def map(self, relative):
        return '%s/%s' % (self.root, relative)


@click.group('banner')
@click.option('--banner-root', help='Root URL for all Banner requests',
              default='https://www5.mun.ca/admit', show_default=True)
@click.option('--ca-bundle', help='path to CA certificate bundle')
@click.option('--credentials', help='file containing username and password',
              type=click.File(), default='credentials.yaml', show_default=True)
@click.option('--term', help='e.g., 201601 for Fall 2016',
              default=term, show_default=True)
def cli(banner_root, ca_bundle, credentials, term):
    """Pull data directly from Banner."""

    import yaml

    urls = urlmapper(banner_root)
    credential = yaml.load(credentials)

    try:
        global browser

        browser = login(credential, urls, ca_bundle)
        browser.set_term(term, urls)

    except BaseException as e:
        import sys
        sys.stderr.write('Error: %s\n' % e)
        return


@cli.command()
def check():
    """Test the connection to Banner."""

    print('Login successful.')


#import getpass
#import importlib
#import logging
#import mechanicalsoup
#import os
#import requests
#import sys
#import traceback
#
#
#    crn = subparsers.add_parser('crn', help='find course CRN from Banner')
#    crn.add_argument('subject', help='academic subject (e.g., ENGI)')
#    crn.add_argument('course_number', help='course number (e.g., 3891)')
#
#    classlist = subparsers.add_parser('classlist', help='fetch class list')
#    classlist.add_argument('crn', help='Course Registration Number',
#                           nargs='+')
#
#    transcript = subparsers.add_parser('transcript', help='fetch transcript')
#    transcript.add_argument('--all', '-a', action='store_true',
#                            help="fetch entire class' transcripts")
#    transcript.add_argument('id', nargs='?',
#                            help="fetch only this student's transcript")


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


def login(credential, urls, ca_bundle):
    import logging
    import mechanicalsoup

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
