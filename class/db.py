# vim: set fileencoding=utf8

import collections
from datetime import date, datetime
from peewee import *

from . import config


providers = {
    'mysql': MySQLDatabase,
    'postgres': PostgresqlDatabase,
    'sqlite': SqliteDatabase,
}

(provider, database) = config.database.split('://')
db = providers[provider](database)


class Instructor(Model):
    username = CharField(unique=True, index=True)
    name = TextField()
    pw_hash = TextField(null=True)
    ta = BooleanField()
    groups = set()

    class Meta:
        database = db

    def email(self):
        return '%s@mun.ca' % self.username

    def role(self):
        return 'TA' if self.ta else 'instructor'

    def __str__(self):
        return '%s (%s)' % (self.name, self.username)

    def __repr__(self):
        return '%s: %s (%s)' % (self.username, self.name, self.role())


class Student(Model):
    username = CharField(unique=True, index=True)
    student_id = IntegerField(unique=True, primary_key=True)
    forename = TextField()
    initial = FixedCharField(null=True)
    surname = TextField()
    pw_hash = TextField(null=True)
    graduate_student = BooleanField(default=False)
    transcript_fetched = DateTimeField(null=True)

    class Meta:
        database = db

    def email(self):
        return '%s@mun.ca' % self.username

    def group(self):
        # TODO: figure out why .desc() doesn't do what we want it to do
        groups = sorted(self.groups, key=lambda g: g.group_id,
                        reverse=True)

        if len(groups) == 0:
            return None
        else:
            return groups[0].group

    # TODO: stop trying to separate forenames from surnames, just use `name`
    def name(self):
        return '%s %s' % (self.forename, self.surname)

    def __str__(self):
        return '%s %s (%s)' % (self.forename, self.surname, self.username)

    def __repr__(self):
        return '%s (%s %s: %s)' % (
            self.username, self.forename, self.surname, self.student_id)


class LabGroup(Model):
    number = PrimaryKeyField()

    def __str__(self):
        members = [m.student.name() for m in self.memberships]
        return 'Group %d (%s)' % (self.number, ', '.join(members))

    class Meta:
        database = db


class GroupMembership(Model):
    group = ForeignKeyField(LabGroup, related_name='memberships')
    student = ForeignKeyField(Student, related_name='groups')

    def __str__(self):
        return '%s: group %d' % (str(self.student), self.group.number)

    def __repr__(self):
        return 'GroupMembership{group: %s, student: %s/%s}' % (
            self.group.number, self.student.username, self.student.student_id
        )

    class Meta:
        database = db


class TranscriptEntry(Model):
    student = ForeignKeyField(Student, related_name='courses')
    year = IntegerField()
    term = IntegerField()
    subject = FixedCharField(4)
    code = FixedCharField(4)
    result = FixedCharField(4)
    mark = IntegerField(null=True)

    class Meta:
        database = db


def close():
    db.close()


def connect():
    db.connect()


def setup():
    db.create_tables([
        GroupMembership, Instructor, LabGroup, Student, TranscriptEntry
    ])
