import parsing.MyPerfectRequest
from data.Ekatalog_db import *
from data.Proxy_db import *
from data.Smartphones_db import *
from parsing import Main, MyPerfectProxy, MyPerfectRequest

with gadgets_db:
    gadgets_db.create_tables([Smartphones])

p = parsing.MyPerfectProxy.Get()
e = Main.Ekatalog()

# i = SmartphonesLinks.select()
#
# for each_i in i:
#     link = each_i.link
#     print(each_i.id)
e.smartphone_specification('https://www.e-katalog.ru/XIAOMI-REDMI-9-NFC-64GB.htm')

# NFC 55 59