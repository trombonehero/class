# vim: set fileencoding=utf8

import collections
from datetime import date, datetime
import config
from peewee import *


providers = {
    'mysql': MySQLDatabase,
    'postgres': PostgresqlDatabase,
    'sqlite': SqliteDatabase,
}

(provider, database) = config.database.split('://')
db = providers[provider](database)


class Student(Model):
    username = CharField(unique = True, index = True)
    student_id = IntegerField(unique = True, primary_key = True)
    forename = TextField()
    initial = FixedCharField(null = True)
    surname = TextField()
    pw_hash = TextField(null = True)
    graduate_student = BooleanField(default = False)

    class Meta:
        database = db

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
        members = [ m.student.name() for m in self.memberships ]
        return 'Group %d (%s)' % (self.number, ', '.join(members))

    class Meta:
        database = db


class GroupMembership(Model):
    group = ForeignKeyField(LabGroup, related_name = 'memberships')
    student = ForeignKeyField(Student, related_name = 'groups')

    def __str__(self):
        return '%s: group %d' % (str(self.student), self.group.number)

    class Meta:
        database = db


def close():
    db.close()

def connect():
    db.connect()

def setup():
    db.create_tables([ GroupMembership, LabGroup, Student ])