import datetime

banner_root = 'https://www5.mun.ca/admit'
credential_file = 'credentials.yaml'

# Default database URL:
database = 'sqlite://class.db'

#
# Terms are numbered as:
#
# 20xx01: Fall 20xx (Sep-Dec 20xx)
# 20xx02: Winter 20xx (Jan-Apr 20xx+1)
# 20xx03: Spring 20xx (May-Aug 20xx+1)
#
today = datetime.date.today()
term = ((today.month - 9) % 12) / 4 + 1
term = '%04d%02d' % (today.year - term / 2, term)

