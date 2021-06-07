from data import Smartphones_db, Pda_db
from parsing import Main
from keyboards import main


class Info:

    def specifications(self):
        ekatalog = Smartphones_db.Smartphones
        pda = Pda_db.SmartphoneSpecificationsPda

        pda_info = pda.select().where(pda.brand == self.brand, pda.model == self.model,
                                      pda.ram == self.ram, pda.storage == self.storage)

        release = os = weight = dimensions = battery = display = cpu = in_stock = cpu_num = core_speed = '---'

        for item in pda_info:
            release = item.release
            os = item.os
            weight = item.weight
            dimensions = item.dimensions
            battery = item.battery
            display = item.display
            cpu = item.cpu

        ekatalog_info = ekatalog.select().where(ekatalog.brand == self.brand, ekatalog.model == self.model,
                                                ekatalog.ram == self.ram, ekatalog.storage == self.storage)

        for item in ekatalog_info:
            in_stock = item.in_stock
            cpu_num = item.cpu_num
            core_speed = item.core_speed

        if self.ram and self.storage:
            first_row = f'{self.brand} {self.model} {self.ram}/{self.storage}'
        elif self.ram and not self.storage:
            first_row = f'{self.brand} {self.model} {self.ram}'
        elif (not self.ram and self.storage) or self.brand == 'Apple':
            first_row = f'{self.brand} {self.model} {self.storage}'
        else:
            first_row = f'{self.brand} {self.model}'

        if in_stock:
            in_stock = 'Есть в продаже'
        else:
            in_stock = 'Нет в продаже'

        cpu = cpu.split(',')
        if len(cpu) > 1:
            cpu = cpu[-1]
        else:
            cpu = cpu[0]

        os = os.split(',')
        if len(os) > 1:
            os = os[-1]
        else:
            os = os[0]

        message = f'{first_row}\n' \
                  f'Релиз: {release}, Экран: {display}\n' \
                  f'ОС: {os}, Аккум.: {battery} мАч\n' \
                  f'Проц.: {cpu}\n' \
                  f'Количество ядер: {cpu_num}, Такт. частота: {core_speed} ГГц\n' \
                  f'Габариты (мм): {dimensions}\n' \
                  f'Вес: {weight} гр., {in_stock}'

        if not ekatalog_info:
            second_markets_update = self.avito_youla_update()
            spec = {'brand': self.brand, 'model': self.model, 'ram': self.ram, 'storage': self.storage,
                    'release': release, 'os': os, 'display': display, 'battery': battery, 'weight': weight,
                    'in_stock': in_stock}
            spec = {**spec, **second_markets_update}
            print('insert in ekat:', spec)
            ekatalog.insert_many(spec).execute()

        prices = self.prices()

        if prices:
            for row in prices:
                message += f'\n{row}'

        return message

    def image(self):
        image = ''
        pda = Pda_db.SmartphoneSpecificationsPda

        pda_info = pda.select().where(pda.brand == self.brand, pda.model == self.model,
                                      pda.ram == self.ram, pda.storage == self.storage)

        for item in pda_info:
            image = item.img

        return image

    def prices(self):
        ekatalog = Smartphones_db.Smartphones

        ekatalog_info = ekatalog.select().where(ekatalog.brand == self.brand, ekatalog.model == self.model,
                                                ekatalog.ram == self.ram, ekatalog.storage == self.storage)

        ozon = yandex = mvideo = eldorado = citilink = svyaznoy = \
            megafon = mts = sber = avito = youla = ''

        message = []

        for item in ekatalog_info:
            ozon = item.max_price_ozon
            yandex = item.max_price_yandex
            mvideo = item.max_price_mvideo
            eldorado = item.max_price_eldorado
            citilink = item.max_price_citilink
            svyaznoy = item.max_price_svyaznoy
            megafon = item.max_price_megafon
            mts = item.max_price_mts
            sber = item.max_price_sbermegamarket
            avito = item.mid_price_avito
            youla = item.mid_price_youla

        if ozon:
            row = f'Озон: {ozon} р'
            message.append(row)

        if yandex:
            row = f'Яндекс: {yandex} р'
            message.append(row)

        if mvideo:
            row = f'М-Видео: {mvideo} р'
            message.append(row)

        if eldorado:
            row = f'Эльдорадо: {eldorado} р'
            message.append(row)

        if citilink:
            row = f'Citilink: {citilink} р'
            message.append(row)

        if svyaznoy:
            row = f'Связной: {svyaznoy} р'
            message.append(row)

        if megafon:
            row = f'Мегафон: {megafon} р'
            message.append(row)

        if mts:
            row = f'МТС: {mts} р'
            message.append(row)

        if sber:
            row = f'СберМегаМаркет: {sber} р'
            message.append(row)

        if avito:
            row = f'Авито: {avito} р (средняя)'
            message.append(row)

        if youla:
            row = f'Юла: {youla} р (средняя)'
            message.append(row)

        if message:
            message.insert(0, '-------- цены --------')

        return message

    def avito_youla_update(self):
        a = Main.Avito(self.brand, self.model, self.storage, self.ram)
        y = Main.Youla(self.brand, self.model, self.storage, self.ram)
        avito_parsing = a.data_mining()
        youla_parsing = y.data_mining()
        result = {**avito_parsing, **youla_parsing}
        return result

    # добавить результат в базу смартфонов с екаталога "smarphones"
    # если происходит парсинг, реализовать выдачу последовательную выдачу финального сообщения:
    # сперва то, что есть в базе (характеристики и имг), после парсинга цены

    def avito_url(self):
        a = Main.Avito(self.brand, self.model, self.ram, self.storage)
        url = a.link

        return url

    def youla_url(self):
        y = Main.Youla(self.brand, self.model, self.ram, self.storage)
        url = y.link

        return url

    def ekatalog_url(self):
        ekatalog = Smartphones_db.Smartphones

        ekatalog_info = ekatalog.get(ekatalog.brand == self.brand, ekatalog.model == self.model,
                                     ekatalog.ram == self.ram, ekatalog.storage == self.storage)

        try:
            url = ekatalog_info.ekatalog_avito
        except:
            url = ''

        return url


class FinaleMessage(Info, main.FinaleKeyboard):
    def __init__(self, brand, model, ram, storage):
        self.brand = brand
        self.model = model
        self.ram = ram
        self.storage = storage
        super().__init__()
