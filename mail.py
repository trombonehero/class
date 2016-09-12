import email.mime.text
import jinja2
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
            sender = db.Instructor.get(db.Instructor.username == args.sender)

    else:
        sender = db.Instructor.get()

    if args.to_all:
        recipients = db.Student.select()

    elif args.to:
        recipients = (
            db.Student.get(username = r) for r in args.to.split(',')
        )

    else:
        sys.stderr.write('Must specify --to or --to-all\n')
        sys.exit(1)

    template = jinja2.Template(f.read())

    for student in recipients:
        content = template.render(student = student)
        message = email.mime.text.MIMEText(content, 'plain', args.encoding)

        message['To'] = student.email()
        message['Subject'] = args.subject
        message['From'] = "%s <%s>" % (sender.name, sender.email())

        if args.test:
            print('---')
            print(message)
            print('---\n')

        else:
            print('Sending to %s:' % student.email())

            smtp = smtplib.SMTP(args.smtp)
            smtp.sendmail(sender, [ student.email() ], message.as_string())
            smtp.quit()
