import re
import statistics

import parsing.MyPerfectRequest
from data.Ekatalog_db import *
from data.Proxy_db import *
from data.Smartphones_db import *
from parsing import Main, MyPerfectProxy, MyPerfectRequest

# with ekatalog_db:
#     ekatalog_db.create_tables([HomePageLinks, SmartphonesLinks, BrandsLinks])
#
# with gadgets_db:
#     gadgets_db.create_tables([Smartphones])

e = Main.Ekatalog()

# e.main_page()
# mobiles = HomePageLinks.get(HomePageLinks.section == 'Мобильные')
# print(mobiles.link)
# e.brands_links(mobiles.link)
# print(mobiles.link_all)
# e.smartphones_links(mobiles.link_all)

db = SmartphonesLinks.select()
db2 = Smartphones

for x in db:
    link = x.link

    try:
        double = db2.get(db2.url_ekatalog == link)
    except:
        double = ''

    if not double:
        print('\n', x.model, link)
        e.smartphone_specification(link)
    else:
        continue

# a = Main.Avito('Xiaomi', 'Mi 10T', '128', '8', 1)
# y = Main.Youla('Xiaomi', 'Mi 10T', '128', '8', 1)
# a.data_mining()
# y.data_mining()