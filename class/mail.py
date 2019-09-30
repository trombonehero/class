import click


@click.command('mail')
@click.argument('subject')
@click.option('-f', '--file', type=click.File(), help='File containing message')

@click.option('--test', is_flag=True, help="Format message but don't send it.")

@click.option('--to', help='Username(s) to send to', metavar="USERNAME")
@click.option('--to-all', is_flag=True, help='Send to all')
@click.option('--filter', help='SQL filter for --to-all', metavar="SQL")
@click.option('--sender', metavar="USERNAME",
              help='Username of instructor sending mail')

@click.option('--encoding', help='Text encoding ("ascii" or "utf-8")',
              metavar='ENC', default='utf-8', show_default=True)
@click.option('--smtp', help='SMTP server', metavar='HOSTNAME',
              default='smtp.mun.ca', show_default=True)

@click.pass_context
def cli(ctx, subject, to, to_all, filter, sender, encoding, smtp, test, file):
    """Send email to the class or individual students."""

    import jinja2
    import sys

    from . import db

    try:
        if sender:
            sender = db.Instructor.get(db.Instructor.username==sender)

        else:
            import peewee
            sender = db.Instructor.get()

    except Exception as e:
        sys.stderr.write('Error: ')

        if not sender:
            sys.stderr.write('--sender not specified and ')


        sys.stderr.write('failed to look up instructor')
        sys.exit(1)

    if to_all:
        import peewee
        recipients = (
                db.Student.select()
                          .join(db.GroupMembership, peewee.JOIN.LEFT_OUTER)
        )

        if filter:
            recipients = recipients.where(db.SQL(filter))

    elif to:
        recipients = (db.Student.get(username=u) for u in to.split(','))

    else:
        sys.stderr.write('Must specify --to or --to-all\n')
        sys.exit(1)

    template = jinja2.Template(file.read())
    send_mail(sender, recipients, subject, template, encoding, test, smtp)


class SMTPSender:
    def __init__(self, server):
        import smtplib
        self.smtp = smtplib.SMTP(server)

    def done(self):
        return self.smtp.quit()

    def send(self, sender, recipient, message):
        print('Sending to %s' % recipient)
        self.smtp.sendmail(sender, [ recipient ], message.as_string())


class TestSender:
    def done(self):
        pass

    def send(self, sender, recipient, message):
        print('---')
        print(message)
        print('---\n')


def send_mail(sender, recipients, subject, template, encoding, test, smtp):
    import email.mime.text

    send = TestSender() if test else SMTPSender(smtp)

    for student in recipients:
        content = template.render(student = student)
        message = email.mime.text.MIMEText(content, 'plain', encoding)

        message['To'] = student.email()
        message['Cc'] = sender.email()
        message['Subject'] = subject
        message['From'] = "%s <%s>" % (sender.name, sender.email())

        send.send(sender.email(), student.email(), message)

    send.done()
