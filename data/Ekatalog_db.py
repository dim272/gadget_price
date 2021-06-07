from peewee import *
from peewee import CharField

ekatalog_db = SqliteDatabase('data/ekatalog.db')


class HomePageLinks(Model):
    id = PrimaryKeyField(unique=True)
    section = CharField(null=True)
    link = CharField(null=True)
    link_all = CharField(null=True)
    updated: CharField = CharField(null=True)

    class Meta:
        database = ekatalog_db


class SmartphonesLinks(Model):
    id = PrimaryKeyField(unique=True)
    model = CharField(null=True)
    link = CharField(null=True)
    img = CharField(null=True)
    updated = CharField(null=True)

    class Meta:
        database = ekatalog_db


class BrandsLinks(Model):
    id = PrimaryKeyField(unique=True)
    brand = CharField(null=True)
    link = CharField(null=True)
    updated = CharField(null=True)

    class Meta:
        database = ekatalog_db
