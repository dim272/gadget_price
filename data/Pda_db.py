from peewee import *

pda_db = SqliteDatabase('data/pda.db')


class CategoriesLinksPda(Model):
    id = PrimaryKeyField(unique=True)
    category = CharField(null=True)
    link = CharField(null=True)
    updated = CharField(null=True)

    class Meta:
        database = pda_db


class BrandsLinksPda(Model):
    id = PrimaryKeyField(unique=True)
    category = CharField(null=True)
    brand = CharField(null=True)
    link = CharField(null=True)
    updated = CharField(null=True)

    class Meta:
        database = pda_db


class SmartphonesLinksPda(Model):
    id = PrimaryKeyField(unique=True)
    brand = CharField(null=True)
    model = CharField(null=True)
    link = CharField(null=True)
    img = CharField(null=True)
    updated = CharField(null=True)

    class Meta:
        database = pda_db


class SmartphoneSpecificationsPda(Model):
    id = PrimaryKeyField(unique=True)
    brand = CharField(null=True)
    model = CharField(null=True)
    img = CharField(null=True)
    release = CharField(null=True)
    os = CharField(null=True)
    battery = CharField(null=True)
    dimensions = CharField(null=True)
    weight = CharField(null=True)
    ram = CharField(null=True)
    storage = CharField(null=True)
    display = CharField(null=True)
    cpu = CharField(null=True)
    core_speed = CharField(null=True)
    updated = CharField(null=True)

    class Meta:
        database = pda_db
