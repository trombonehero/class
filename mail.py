import email.mime.text
import smtplib
import sys


def setup_argparse(parser):
    parser.add_argument('--smtp', help = 'SMTP server', default = 'smtp.mun.ca')
    parser.add_argument('--test', help = "format message but don't send",
            action = 'store_true')

    parser.add_argument('--to', help = 'student(s) to send to', nargs = '*')
    parser.add_argument('--to-all', help = 'send to all', action = 'store_true')
    parser.add_argument('--sender', help = "sender's address", required = True)
    parser.add_argument('--subject', help = 'message subject', required = True)

    parser.add_argument('filename', nargs = '?', default = '-')


def run(args, db):
    f = sys.stdin if args.filename == '-' else open(args.filename)

    if args.to_all:
        recipients = [ s.email() for s in db.Student.select() ]

    else:
        recipients = [
            r if '@' in r
                else db.Student.get(username = r).email()
                for r in args.to
        ]

    message = email.mime.text.MIMEText(f.read(), 'plain', 'utf-8')
    message['Subject'] = args.subject
    message['From'] = args.sender

    # Use BCC to hide multiple recipients' addresses from each other:
    if len(recipients) == 1:
        message['To'] = recipients[0]

    else:
        message['To'] = args.sender
        message['Bcc'] = ','.join(recipients)

    if args.test:
        print(message)

    else:
        print('Sending to: %s' % ' '.join(recipients))

        smtp = smtplib.SMTP(args.smtp)
        smtp.sendmail(args.sender, recipients, message.as_string())
        smtp.quit()
