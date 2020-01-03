import click
import peewee


@click.command('remove')
@click.option('--instructor', is_flag=True,
              help='Is this person a TA or instructor (vs a student)?')
@click.argument('user_id', type=int, nargs=-1, required=True)
@click.pass_obj
def cli(db, user_id, instructor):
    """Remove a student or instructor/TA from the class."""

    if instructor:
        db.Instructor.delete().where(db.Instructor.id.in_(user_id)).execute()
    else:
        db.Student.delete().where(db.Student.student_id.in_(user_id)).execute()
