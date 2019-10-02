import click


@click.command('redact')
@click.pass_obj
def cli(db):
    """Redact some personally-identifying information.

    This command does NOT fully "anonymize" the data: the resulting database
    still can't be shared.
    """

    query = db.Student.update(username=db.Student.student_id,
                              forename='',
                              initial='',
                              surname='')

    count = query.execute()
    print(f'Redacted name and username for {count} students')
