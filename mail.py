import email.mime.text
import smtplib
import sys


def setup_argparse(parser):
    parser.add_argument('--encoding', help = 'test encoding (default: utf-8)',
            default = 'utf-8')
    parser.add_argument('--smtp', help = 'SMTP server', default = 'smtp.mun.ca')
    parser.add_argument('--test', help = "format message but don't send",
            action = 'store_true')

    parser.add_argument('--to', help = 'student(s) to send to')
    parser.add_argument('--to-all', help = 'send to all', action = 'store_true')
    parser.add_argument('--sender', help = "sender")

    parser.add_argument('-f', '--filename', default = '-',
            help = 'file containing message (or stdin)')

    parser.add_argument('subject', help = 'message subject')


def run(args, db):
    f = sys.stdin if args.filename == '-' else open(args.filename)

    if args.sender:
        if '@' in args.sender: sender = args.sender
        else:
            i = db.Instructor.get(db.Instructor.username == args.sender)
            sender = i.username

    else:
        sender = db.Instructor.get().username

    if args.to_all:
        recipients = [ s.email() for s in db.Student.select() ]

    elif args.to:
        recipients = [
            r if '@' in r
                else db.Student.get(username = r).email()
                for r in args.to.split(',')
        ]

    else:
        sys.stderr.write('Must specify --to or --to-all\n')
        sys.exit(1)

    message = email.mime.text.MIMEText(f.read(), 'plain', args.encoding)
    message['Subject'] = args.subject
    message['From'] = sender

    # Use BCC to hide multiple recipients' addresses from each other:
    if len(recipients) == 1:
        message['To'] = recipients[0]

    else:
        message['To'] = sender
        message['Bcc'] = ','.join(recipients)

    if args.test:
        print(message)

    else:
        print('Sending to: %s' % ' '.join(recipients))

        smtp = smtplib.SMTP(args.smtp)
        smtp.sendmail(sender, recipients, message.as_string())
        smtp.quit()
