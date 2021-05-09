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
    weight = CharField(null=True)
    in_stock = BooleanField(null=True)
    max_price_ozon = CharField(null=True)
    min_price_ozon = CharField(null=True)
    max_price_yandex = CharField(null=True)
    min_price_yandex = CharField(null=True)
    max_price_mvideo = CharField(null=True)
    min_price_mvideo = CharField(null=True)
    max_price_eldorado = CharField(null=True)
    min_price_eldorado = CharField(null=True)
    max_price_citilink = CharField(null=True)
    min_price_citilink = CharField(null=True)
    max_price_svyaznoy = CharField(null=True)
    min_price_svyaznoy = CharField(null=True)
    max_price_megafon = CharField(null=True)
    min_price_megafon = CharField(null=True)
    max_price_mts = CharField(null=True)
    min_price_mts = CharField(null=True)
    max_price_sbermegamarket = CharField(null=True)
    min_price_sbermegamarket = CharField(null=True)
    max_price_avito = CharField(null=True)
    min_price_avito = CharField(null=True)
    max_price_youla = CharField(null=True)
    min_price_youla = CharField(null=True)
    updated = DateField(null=True)

    class Meta:
        database = gadgets_db
        order_by = 'brand'
