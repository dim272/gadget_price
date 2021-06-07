from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import data.Smartphones_db
from data import Smartphones_db, Pda_db

'''

[Apple] > [iPhone 11] > [128]
[Xiaomi] > [Redmi Note 9] > [4] > [64]

'''


class Choice:
    def __init__(self):
        self.__page = 1
        self._items_used = 0

    def __get_len_items(self):
        return len(self.items)

    def __rows_we_need(self):
        num = self.__get_len_items()

        if num % 3 != 0:
            result = (num // 3) + 1
        else:
            result = int(num / 3)

        return result

    @staticmethod
    def _breadcrumbs_button_generator(select, item):
        cd = f'select:{select.lower()}:item:{item}'
        btn = InlineKeyboardButton(text=item, callback_data=cd)
        return btn

    def __button_generator(self, item):
        class_name = self.__class__.__name__
        cd = f'select:{class_name.lower()}:item:{item}'
        btn = InlineKeyboardButton(text=item, callback_data=cd)
        return btn

    @staticmethod
    def __error_button():
        return InlineKeyboardButton(text='Ошибка', callback_data='select:control:item:start')

    @staticmethod
    def _start_button():
        return InlineKeyboardButton(text='< Начало', callback_data='select:control:item:start')

    def __next_page_button(self):
        class_name = self.__class__.__name__
        cd = f'select:{class_name.lower()}:item:next'
        btn = InlineKeyboardButton(text='>', callback_data=cd)
        return btn

    def __prev_page_button(self):
        class_name = self.__class__.__name__
        cd = f'select:{class_name.lower()}:item:prev'
        btn = InlineKeyboardButton(text='<', callback_data=cd)
        return btn

    def __breadcrumbs_row_generator(self):
        class_name = self.__class__.__name__
        breadcrumbs_row = []

        if class_name != 'Brand':
            start_button = self._start_button()
            breadcrumbs_row.append(start_button)
            brand_name = self.brand
            brand_button = self._breadcrumbs_button_generator('brand', brand_name)
            breadcrumbs_row.append(brand_button)
            if class_name == 'Ram':
                model_name = self.model
                model_button = self._breadcrumbs_button_generator('model', model_name)
                breadcrumbs_row.append(model_button)
            if class_name == 'Storage':
                model_name = self.model
                model_button = self._breadcrumbs_button_generator('model', model_name)
                breadcrumbs_row.append(model_button)
                ram = self.ram
                ram_button = self._breadcrumbs_button_generator('ram', ram)
                breadcrumbs_row.append(ram_button)

        return breadcrumbs_row

    def __row_generator(self, row_number):
        row = []
        counter = 1
        while counter <= 3 and self._items_used < self.__get_len_items():
            item = self.items[self._items_used]
            btn = self.__button_generator(item)

            if counter == 1:
                if row_number == 1:
                    if self._items_used == 0:
                        row.append(btn)
                        counter += 1
                        self._items_used += 1
                    else:
                        row.append(self.__prev_page_button())
                        counter += 1
                else:
                    row.append(btn)
                    counter += 1
                    self._items_used += 1
            elif counter == 2:
                row.append(btn)
                counter += 1
                self._items_used += 1
            elif counter == 3:
                if row_number == 3 and self._items_used == (self.__get_len_items() - 1):
                    row.append(btn)
                    counter += 1
                    self._items_used += 1
                elif row_number == 3:
                    row.append(self.__next_page_button())
                    counter += 1
                else:
                    row.append(btn)
                    counter += 1
                    self._items_used += 1
            else:
                row.append(self.__error_button())
                counter += 1

        return row

    def keyboard_generator(self):
        inline_keyboard = []
        breadcrumbs = self.__breadcrumbs_row_generator()
        row_number = 1

        if breadcrumbs:
            inline_keyboard.append(breadcrumbs)

        if self.__rows_we_need() > 3:
            rows_we_need = 3
        else:
            rows_we_need = self.__rows_we_need()

        while row_number <= rows_we_need:
            row = self.__row_generator(row_number)
            inline_keyboard.append(row)
            row_number += 1

        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        return keyboard

    def next_page(self):
        self.__page += 1

    def prev_page(self):
        if self.__page != 1:
            self.__page -= 1
            if self.__page == 1:
                self._items_used -= 15
            else:
                self._items_used -= 14
        else:
            self._items_used -= 8


class Brand(Choice):
    def __init__(self):
        self.items = self.__get_top_brands()
        super().__init__()

    @staticmethod
    def __get_top_brands():
        db = Smartphones_db.TopBrands
        select = db.select(db.brand).order_by(db.top.desc())
        brand_list = []
        for each in select:
            brand_list.append(each.brand)
        return brand_list

    @staticmethod
    def increase_top_value(brand_name):
        db = Smartphones_db.TopBrands
        select = db.get(db.brand.contains(brand_name.strip()))
        top = select.top
        select.update(top=top).execute()


class Model(Choice):
    def __init__(self, brand):
        self.brand = brand
        self.items = self.__get_models()
        super().__init__()

    def __get_models(self):
        db = Pda_db.SmartphoneSpecificationsPda
        select = db.select(db.model).where(db.brand == self.brand)
        model_list = []
        for each in select:
            model = each.model
            if model not in model_list:
                model_list.append(model)
        return model_list


class Ram(Choice):
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model
        self.items = self.__get_ram()
        super().__init__()

    def __get_ram(self):
        db = Pda_db.SmartphoneSpecificationsPda
        select = db.select(db.ram).where(db.brand == self.brand, db.model == self.model)
        ram_list = []
        for each in select:
            try:
                ram = each.ram
            except:
                continue
            if ram not in ram_list:
                ram_list.append(ram)

        return ram_list


class Storage(Choice):
    def __init__(self, brand, model, ram):
        self.brand = brand
        self.model = model
        self.ram = ram
        self.items = self.__get_storage()
        super().__init__()

    def __get_storage(self):
        db = Pda_db.SmartphoneSpecificationsPda
        select = db.select(db.storage).where(db.brand == self.brand, db.model == self.model, db.ram == self.ram)
        storage_list = []
        for each in select:
            try:
                storage = each.storage
            except:
                continue
            if storage not in storage_list:
                storage_list.append(storage)

        return storage_list


class Breadcrumbs(Choice):
    def __init__(self, ):
        super().__init__()

    def breadcrumbs_keyboard(self, brand, model, ram, storage):
        specifications = [['brand', brand], ['model', model], ['ram', ram], ['storage', storage]]
        breadcrumbs = []
        start_button = self._start_button()
        breadcrumbs.append(start_button)
        for each in specifications:
            select = each[0]
            item = each[1]
            button = self._breadcrumbs_button_generator(select, item)
            breadcrumbs.append(button)

        return breadcrumbs


class FinaleKeyboard(Breadcrumbs):

    def __init__(self):
        super().__init__()

    def links_to_markets(self):
        db = data.Smartphones_db.Smartphones
        search = db.select().where(db.brand == self.brand, db.model == self.model,
                                   db.ram == self.ram, db.storage == self.storage)

        links = {}

        if search:

            if len(search) > 1:
                search = db.select().where(db.brand == self.brand, db.model == self.model,
                                           db.ram == self.ram, db.storage == self.storage, db.nfc == 0)

            for item in search:
                ekatalog = item.url_ekatalog
                if ekatalog:
                    links['E-Katalog'] = ekatalog
                avito = item.url_avito
                if avito:
                    links['Avito'] = avito
                youla = item.url_youla
                if youla:
                    links['Youla'] = youla

        return links

    @staticmethod
    def market_button_generator(name, link):
        return InlineKeyboardButton(text=name, url=link)

    def generate(self):
        breadcrumbs = self.breadcrumbs_keyboard(self.brand, self.model, self.ram, self.storage)
        inline_keyboard = [breadcrumbs]

        links = self.links_to_markets()
        if links:
            links_block = []
            for item in links:
                link = links.get(item)
                market_button = self.market_button_generator(item, link)
                links_block.append(market_button)
            inline_keyboard.append(links_block)

        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

        return keyboard
