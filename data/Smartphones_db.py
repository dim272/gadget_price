from peewee import *

gadgets_db = SqliteDatabase('data/gadgets.db')


class Smartphones(Model):
    id = PrimaryKeyField(unique=True)
    brand = CharField()
    model = CharField()
    release = CharField(null=True)
    os = CharField(null=True)
    display = CharField(null=True)
    storage = CharField(null=True)
    ram = CharField(null=True)
    cpu_num = CharField(null=True)
    core_speed = CharField(null=True)
    battery = CharField(null=True)
    in_stock = BooleanField(null=True)
    price_ozon = CharField(null=True)
    price_yandex = CharField(null=True)
    price_mvideo = CharField(null=True)
    price_eldorado = CharField(null=True)
    price_citilink = CharField(null=True)
    price_svyaznoy = CharField(null=True)
    price_megafon = CharField(null=True)
    price_mts = CharField(null=True)
    price_sbermegamarket = CharField(null=True)
    price_avito = CharField(null=True)
    price_youla = CharField(null=True)
    updated = DateField(null=True)

    class Meta:
        database = gadgets_db
        order_by = 'brand'
