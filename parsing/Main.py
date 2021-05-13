import re
from statistics import mean
from datetime import date, datetime

from parsing import MyPerfectRequest
from data import Ekatalog_db, Smartphones_db, Pda_db


class Ekatalog:

    def main_page(self):
        request = MyPerfectRequest.Get(use_proxy=True, android_headers=True)
        url = 'https://www.e-katalog.ru/'
        soup = request.soup(url)
        today = date.today().strftime("%d.%m.%Y")
        db = Ekatalog_db.HomePageLinks

        try:
            cache = soup.find_all('div', class_='main_slide')
        except:
            cache = False

        if cache:
            for item in cache:
                a = item.find('a')
                section = a.text
                href = a['href'].replace('/', '')
                link = url + href

                double = db.select().where(db.link == link)
                if not double:
                    l_all = self.all_link_of_section(link)
                    db.create(section=section, link=link, link_all=l_all, updated=today)

    @staticmethod
    def all_link_of_section(url):
        home = 'https://www.e-katalog.ru'
        request = MyPerfectRequest.Get(use_proxy=True, android_headers=True)
        soup = request.soup(url)
        try:
            a = soup.find('div', class_='all-link').find('a')
            href = a['href']
            link = home + href
        except:
            link = ''

        return link

    @staticmethod
    def find_next_page_link(soup):
        pattern = 'https://www.e-katalog.ru'

        try:
            next_page = soup.find('a', id='pager_next')
            href = next_page.get('href')
            link = pattern + href
        except:
            link = False

        return link

    @staticmethod
    def brands_links(url):
        pattern = 'https://www.e-katalog.ru'
        r = MyPerfectRequest.Get(use_proxy=True, android_headers=True)
        soup = r.soup(url)
        today = date.today().strftime("%d.%m.%Y")
        db = Ekatalog_db.BrandsLinks

        try:
            links = soup.find('div', class_='brands-list').find_all('a')
        except:
            links = []

        if links:
            for each in links:
                brand = each.text
                try:
                    href = each.get('href') if 'list' in each.get('href') else ''
                except:
                    href = False

                if href:
                    link = pattern + href

                    double = db.select().where(db.link == link)
                    if not double:
                        db.create(brand=brand, link=link, updated=today)
                else:
                    continue

    def smartphones_links(self, url):
        pattern = 'https://www.e-katalog.ru'
        r = MyPerfectRequest.Get(use_proxy=True, android_headers=True)
        db = Ekatalog_db.SmartphonesLinks
        today = date.today().strftime("%d.%m.%Y")

        while True:
            soup = r.soup(url)
            items = soup.find_all('table', class_='model-short-block')

            if not items:
                break

            for item in items:
                try:
                    a = item.find('a', class_='model-short-title')
                    href = a.get('href')
                    link = pattern + href
                except:
                    continue

                try:
                    img = item.find('div', class_='list-img').find('img', src=True).get('src')
                    img = pattern + img
                except:
                    img = ''

                text_list = a.find_all('span')
                model_name = text_list[0].text
                try:
                    storage = text_list[1].text
                    model = model_name + ' ' + storage
                except:
                    model = model_name

                double = db.select().where(db.link == link)

                if not double:
                    db.create(model=model, link=link, img=img, updated=today)
                else:
                    continue

            next_page = self.find_next_page_link(soup)

            if next_page:
                url = next_page
            else:
                break

    @staticmethod
    def _brand_name_finder(soup):
        brand = ''

        try:
            script_list = soup.find('head').find_all('script')
        except:
            script_list = []

        for script in script_list:
            this_what_we_need = re.search(r'\bdataLayer\b', str(script))
            if this_what_we_need:
                a = str(script).split('"brand":"')
                b = a[1].split('"')
                brand = b[0]
                break
            else:
                continue

        return brand

    @staticmethod
    def _model_name_finder(soup, brand_name):
        brand_part_list = brand_name.split(' ')

        try:
            title = soup.find('div', id='top-page-title').get('data-title')
        except:
            title = ''

        if title:
            a = title.split('<span')
            b = a[0].strip().split(' ')

            if len(brand_part_list) > 1:
                for brand_part in brand_part_list:
                    b.remove(brand_part)
            else:
                b.remove(brand_name)

            if 'nfc' in a[0].lower():
                b.remove('NFC')

            model_name = ' '.join(b)
        else:
            model_name = ''

        return model_name

    @staticmethod
    def _display_parsing(each_spec):
        try:
            search_display = each_spec.get('title').split(',')
            display = re.sub("[^0-9.,]", "", search_display[0])
            display = display.replace(',', '.')
        except:
            display = ''

        return display

    @staticmethod
    def _storage_parsing(each_spec):
        try:
            search_storage = each_spec.get('title').split(',')
            storage = re.sub("[^0-9]", "", search_storage[0])
        except:
            storage = ''

        return storage

    @staticmethod
    def _ram_parsing(each_spec):
        try:
            search_ram = each_spec.get('title').split(',')
            ram = re.sub("[^0-9]", "", search_ram[1])
        except:
            ram = ''

        return ram

    @staticmethod
    def _num_cores_parsing(each_spec):
        try:
            search_core = each_spec.get('title').split(',')
            num_cores = re.sub("[^0-9.,]", "", search_core[0])
            num_cores = num_cores.replace(',', '.')
        except:
            num_cores = ''

        return num_cores

    @staticmethod
    def _core_speed_parsing(each_spec):
        try:
            search_speed = each_spec.get('title').split(',')
            core_speed = re.sub("[^0-9.,]", "", search_speed[1])
            core_speed = core_speed.replace(',', '.')
        except:
            core_speed = ''

        return core_speed

    @staticmethod
    def _battery_parsing(each_spec):
        try:
            search_battery = each_spec.get('title')
            battery = re.sub("[^0-9.]", "", search_battery)
        except:
            battery = ''

        return battery

    @staticmethod
    def _weight_parsing(each_spec):
        try:
            search_weight = each_spec.get('title')
            weight = re.sub("[^0-9.]", "", search_weight)
        except:
            weight = ''

        return weight

    @staticmethod
    def _tags_founder(soup):
        try:
            specifications = soup.find('div', class_='m-c-f1')
        except:
            specifications = ''

        try:
            required_blocks1 = specifications.find_all('span')
        except:
            required_blocks1 = ''

        try:
            required_blocks2 = specifications.find_all('a')
        except:
            required_blocks2 = ''

        required_blocks = required_blocks1 + required_blocks2

        return required_blocks

    def _release_parsing(self, soup):
        required_blocks = self._tags_founder(soup)
        release = None

        if required_blocks:
            for block in required_blocks:
                its_release = re.search(r'\bгод\b', block.text)
                if its_release:
                    release = re.sub("[^0-9]", "", block.text)
                    break
        return release

    def _nfc_parsing(self, soup):
        required_blocks = self._tags_founder(soup)

        nfc = 0

        if required_blocks:
            for block in required_blocks:
                its_nfc = re.search(r'\bNFC\b', block.text)
                if its_nfc:
                    nfc = 1
                    break
        return nfc

    @staticmethod
    def _is_in_stock(soup):
        in_stock = True
        try:
            top_block = soup.find('div', class_='desc-short-prices')
        except:
            top_block = ''
            in_stock = False

        not_in_stock = top_block.select('.desc-not-avail')
        expected_on_sale = top_block.select('.or')

        if not_in_stock or expected_on_sale:
            in_stock = False

        try:
            ref = soup.find('div', class_="wb-REF")
        except:
            ref = False

        if ref:
            in_stock = False

        return in_stock

    @staticmethod
    def _more_button_finder(soup):
        try:
            more_btn = soup.find('table', id='item-wherebuy-table') \
                .next_sibling.find('div', class_='list-more-div-small') \
                .get('jsource')
            url_pattern = more_btn.replace('amp;', '')
            url_pieces = url_pattern.split('_start_=')
            new_url = url_pieces[0] + '_start_=1&p_end_=100'
        except:
            new_url = ''

        return new_url

    @staticmethod
    def _price_parsing_sorter(list_):
        new_data = {}
        for one_dict in list_:
            for key in one_dict:
                try:
                    val = new_data[key]
                    new_data[key] = val + [one_dict[key]]
                except KeyError:
                    new_data[key] = [one_dict[key]]

        result = {}
        for key in new_data:
            max_price = max(new_data[key])
            min_price = min(new_data[key])
            max_key = 'max_' + key
            min_key = 'min_' + key

            result[max_key] = max_price
            result[min_key] = min_price

        return result

    def _price_parsing(self, soup):
        try:
            where_buy = soup.find('table', id="item-wherebuy-table")
            shops = where_buy.find_all("tr", {"class": True})
        except:
            shops = []

        favorite_shops = ['mts.ru', 'svyaznoy.ru', 'citilink.ru', 'м.видео', 'megafon.ru', 'eldorado.ru',
                          'ozon.ru', 'sbermegamarket.ru']

        result = []

        for shop in shops:
            try:
                shop_name = shop.find('a', class_="it-shop").text
            except:
                continue

            if shop_name.lower() not in favorite_shops:
                continue

            shop_name_dot_ru = re.search(r'\bru\b', shop_name)
            if shop_name_dot_ru:
                dict_key = 'price_' + shop_name.lower().replace('.ru', '')
            else:
                dict_key = 'price_mvideo'

            try:
                price_block = shop.find('td', class_="where-buy-price").text
                price = re.sub("[^0-9]", "", price_block)
            except:
                continue

            result.append({dict_key: price})

        if result:
            sorted_results = self._price_parsing_sorter(result)
        else:
            sorted_results = {}

        return sorted_results

    def _price_parsing_more_button(self, soup):
        try:
            where_buy = soup.find('table')
            shops = where_buy.find_all("tr", {"class": True})
        except:
            shops = []

        result = []

        favorite_shops = ['mts.ru', 'svyaznoy.ru', 'citilink.ru', 'м.видео', 'megafon.ru', 'eldorado.ru',
                          'ozon.ru', 'sbermegamarket.ru']

        for shop in shops:
            try:
                shop_name = shop.find('h3').next_sibling.find('a').text
            except AttributeError:
                try:
                    shop_name = shop.find('h3').parent.next_sibling.find('a').text
                except AttributeError:
                    continue

            if shop_name.lower() not in favorite_shops:
                continue

            shop_name_dot_ru = re.search(r'\bru\b', shop_name)
            if shop_name_dot_ru:
                dict_key = 'price_' + shop_name.lower().replace('.ru', '')
            else:
                dict_key = 'price_mvideo'

            blocks = shop.find_all('td')
            price_block = blocks[3]
            price = re.sub("[^0-9]", "", price_block.text)

            result.append({dict_key: price})

        if result:
            sorted_results = self._price_parsing_sorter(result)
        else:
            sorted_results = {}

        return sorted_results

    def smartphone_specification(self, url):
        r = MyPerfectRequest.Get(use_proxy=True, android_headers=True)
        soup = r.soup(url)

        brand = self._brand_name_finder(soup)
        model = self._model_name_finder(soup, brand)
        today = date.today().strftime("%d.%m.%Y")

        try:
            db = Ekatalog_db.SmartphonesLinks
            row = db.get(db.link == url)
            img = row.img
        except:
            img = ''

        spec_dict = {'brand': brand, 'model': model, 'url_ekatalog': url, 'updated': today, 'img': img}

        try:
            specifications = soup.find('div', class_='m-c-f2').select('.m-s-f3')
        except:
            specifications = []

        if specifications:
            for each_spec in specifications:

                its_display = re.search(r'\bЭкран\b', each_spec.text)
                if its_display:
                    display = self._display_parsing(each_spec)
                    spec_dict['display'] = str(display)
                    continue

                its_storage = re.search(r'\bПамять\b', each_spec.text)
                if its_storage:
                    storage = self._storage_parsing(each_spec)
                    ram = self._ram_parsing(each_spec)
                    spec_dict['storage'] = str(storage)
                    spec_dict['ram'] = str(ram)
                    continue

                its_cpu = re.search(r'\bПроцессор\b', each_spec.text)
                if its_cpu:
                    cpu_num = self._num_cores_parsing(each_spec)
                    core_speed = self._core_speed_parsing(each_spec)
                    spec_dict['cpu_num'] = str(cpu_num)
                    spec_dict['core_speed'] = str(core_speed)
                    continue

                its_battery = re.search(r'\bЕмкость батареи\b', each_spec.text)
                if its_battery:
                    battery = self._battery_parsing(each_spec)
                    spec_dict['battery'] = str(battery)
                    continue

                its_weight = re.search(r'\bВес\b', each_spec.text)
                if its_weight:
                    weight = self._weight_parsing(each_spec)
                    spec_dict['weight'] = str(weight)
                    continue

        release = self._release_parsing(soup)
        if release:
            spec_dict['release'] = str(release)

        nfc = self._nfc_parsing(soup)
        spec_dict['nfc'] = nfc

        in_stock = self._is_in_stock(soup)

        ekatalog_price_dict = {}
        if in_stock:
            new_url = self._more_button_finder(soup)
            if new_url:
                soup_for_price_parsing = r.soup(new_url)
                ekatalog_price_dict = self._price_parsing_more_button(soup_for_price_parsing)
            else:
                ekatalog_price_dict = self._price_parsing(soup)

        if not ekatalog_price_dict:
            in_stock = False
        spec_dict['in_stock'] = bool(in_stock)

        if storage and ram:
            a = Avito(brand, model, storage, ram, nfc)
            avito_price_dict = a.data_mining()
            y = Youla(brand, model, storage, ram, nfc)
            youla_price_dict = y.data_mining()
            youla_avito_price = {**avito_price_dict, **youla_price_dict}
        else:
            youla_avito_price = {}

        price_dict = {**ekatalog_price_dict, **youla_avito_price}

        final_dict = {**spec_dict, **price_dict}

        print(final_dict)
        Smartphones_db.Smartphones.insert_many(final_dict).execute()

    def search(self, brand, model, storage, ram, nfc):
        # 'Xiaomi', 'Redmi Note 9', '64', '3', 0
        db = Smartphones_db.Smartphones
        search = db.get(db.brand == brand, db.model == model, db.storage == storage, db.ram == ram, db.nfc == nfc)

        try:
            updated = search.updated
        except:
            updated = ''

        if updated:
            today = date.today().strftime("%d.%m.%Y")
            s_updated = datetime.strptime(updated, "%d.%m.%Y")
            s_today = datetime.strptime(today, "%d.%m.%Y")
            days_gone = s_today - s_updated
            print('Days gone:', days_gone)

            if days_gone > 2:
                url = search.url
                self.smartphone_specification()


class Avito:
    def __init__(self, brand, model, storage, ram, nfc):
        self.brand = brand
        self.model = model
        self.storage = storage
        self.ram = ram
        self.nfc = nfc
        self.link = self._link_generator()
        self.search_requests = self._different_search_requests()

    def _different_search_requests(self):
        brand = self.brand.lower()
        model = self.model.lower()
        model2 = self.model.lower().replace(' ', '')
        storage = self.storage
        ram = self.ram

        search_requests = []

        v = brand + ' ' + model + ' ' + ram + '/' + storage
        search_requests.append(v)

        v = brand + ' ' + model + ' ' + ram + ' ' + storage
        search_requests.append(v)

        v = brand + ' ' + model + ' ' + ram + 'gb' + '/' + storage + 'gb'
        search_requests.append(v)

        v = brand + ' ' + model + ' ' + ram + 'gb' + ' ' + storage + 'gb'
        search_requests.append(v)

        v = model + ' ' + ram + '/' + storage
        search_requests.append(v)

        v = model + ' ' + ram + ' ' + storage
        search_requests.append(v)

        v = brand + ' ' + model + ' ' + storage
        search_requests.append(v)

        v = model + ' ' + storage
        search_requests.append(v)

        v = brand + ' ' + model2 + ' ' + ram + '/' + storage
        search_requests.append(v)

        v = brand + ' ' + model2 + ' ' + ram + ' ' + storage
        search_requests.append(v)

        v = brand + ' ' + model2 + ' ' + ram + 'gb' + '/' + storage + 'gb'
        search_requests.append(v)

        v = brand + ' ' + model2 + ' ' + ram + 'gb' + ' ' + storage + 'gb'
        search_requests.append(v)

        v = model2 + ' ' + ram + '/' + storage
        search_requests.append(v)

        v = model2 + ' ' + ram + ' ' + storage
        search_requests.append(v)

        v = brand + ' ' + model2 + ' ' + storage
        search_requests.append(v)

        v = model2 + ' ' + storage
        search_requests.append(v)

        return search_requests

    def _link_generator(self):
        # https://m.avito.ru/rossiya/telefony?q=xiaomi%2Bredmi%2Bnote%2B9%2B3gb%2B64gb
        domain = 'https://m.avito.ru/rossiya/telefony?q='
        brand = self.brand.lower()
        model = self.model.replace(' ', '+').lower()
        storage = self.storage + 'gb'
        ram = self.ram + 'gb'

        if brand == 'apple':
            link = domain + brand + '+' + model + '+' + storage
        else:
            link = domain + brand + '+' + model + '+' + ram + '+' + storage
            if self.nfc:
                link = link + '+nfc'

        return link

    @staticmethod
    def _soup(url):
        r = MyPerfectRequest.Get(use_proxy=True, desktop_headers=True)
        soup = r.soup(url)
        return soup

    @staticmethod
    def _find_next_page(soup):
        domain = 'https://m.avito.ru'

        try:
            pages = soup.find('div', 'pagination-pages').find_all('a')
        except:
            pages = []

        if pages:
            a = pages[-1]
            href = a.get('href')
            link = domain + href
        else:
            link = ''

        return link

    def _title_sorting(self, data):
        result = {}

        for d in data:
            title = list(d.keys())[0].lower()
            price = list(d.values())[0]

            for each in self.search_requests:

                search = re.search(each, title)
                if search:
                    if not self.nfc:
                        search_nfc = re.search('nfc', title)
                        if not search_nfc:
                            try:
                                val = result[price]
                            except:
                                val = 0
                            result[price] = val + 1
                    else:
                        try:
                            val = result[price]
                        except:
                            val = 0
                        result[price] = val + 1

        sorted_result = {}

        for w in sorted(result, key=result.get, reverse=True):
            sorted_result[w] = result[w]

        return sorted_result

    def _price_sorting(self, sorted_data):
        max_value = max(list(sorted_data.values()))

        price_list = []
        top_price_list = []

        for d in sorted_data:
            key = d
            val = sorted_data[key]

            if not key or not val:
                continue
            if val == max_value or val == (max_value - 1):
                top_price_list.append(int(key))
                price_list.append(int(key))
            else:
                price_list.append(int(key))

        max_price = max(price_list)
        min_price = min(price_list)
        middle_price = mean(top_price_list)
        middle_price = round(middle_price / 500) * 500

        result = {'max_price_avito': max_price, 'min_price_avito': min_price,
                  'mid_price_avito': middle_price, 'url_avito': self.link}

        return result

    def _data_sorting(self, data):
        # data = [{title: price}]
        sorted_data = self._title_sorting(data)
        if sorted_data:
            sorted_result = self._price_sorting(sorted_data)
        else:
            sorted_result = {}

        return sorted_result

    def data_mining(self):
        result = []
        url = self.link
        while True:
            soup = self._soup(url)

            try:
                items = soup.find_all('div', {'data-marker': 'item'})
            except:
                items = []

            if not items:
                break

            for item in items:
                try:
                    title = item.find('a', {'data-marker': 'item-title'}).find('h3').text
                except:
                    title = ''

                try:
                    price = item.find('span', {'data-marker': 'item-price'}).text
                    price = re.sub("[^0-9]", "", price)
                except:
                    price = ''

                result.append({title: price})

            next_page = self._find_next_page(soup)

            if not next_page or next_page == url:
                break
            else:
                url = next_page
                continue

        sorted_result = self._data_sorting(result)
        if not sorted_result:
            sorted_result = {'url_avito': self.link}

        return sorted_result


class Youla:
    def __init__(self, brand, model, storage, ram, nfc):
        self.brand = brand
        self.model = model
        self.storage = storage
        self.ram = ram
        self.nfc = nfc
        self.link = self._link_generator()
        self.search_requests = self._different_search_requests()

    def _link_generator(self):
        domain = 'https://youla.ru/moskva?q='
        brand = self.brand.lower()
        model = self.model.replace(' ', '+').lower()
        storage = self.storage + 'gb'
        ram = self.ram + 'gb'

        if brand == 'apple':
            link = domain + brand + '+' + model + '+' + storage
        else:
            link = domain + brand + '+' + model + '+' + ram + '+' + storage
            if self.nfc:
                link = link + '+nfc'

        return link

    def _different_search_requests(self):
        brand = self.brand.lower()
        model = self.model.lower()
        model2 = self.model.lower().replace(' ', '')
        storage = self.storage
        ram = self.ram

        search_requests = []

        v = brand + ' ' + model + ' ' + ram + '/' + storage
        search_requests.append(v)

        v = brand + ' ' + model + ' ' + ram + ' ' + storage
        search_requests.append(v)

        v = brand + ' ' + model + ' ' + ram + 'gb' + '/' + storage + 'gb'
        search_requests.append(v)

        v = brand + ' ' + model + ' ' + ram + 'gb' + ' ' + storage + 'gb'
        search_requests.append(v)

        v = model + ' ' + ram + '/' + storage
        search_requests.append(v)

        v = model + ' ' + ram + ' ' + storage
        search_requests.append(v)

        v = brand + ' ' + model + ' ' + storage
        search_requests.append(v)

        v = model + ' ' + storage
        search_requests.append(v)

        v = brand + ' ' + model2 + ' ' + ram + '/' + storage
        search_requests.append(v)

        v = brand + ' ' + model2 + ' ' + ram + ' ' + storage
        search_requests.append(v)

        v = brand + ' ' + model2 + ' ' + ram + 'gb' + '/' + storage + 'gb'
        search_requests.append(v)

        v = brand + ' ' + model2 + ' ' + ram + 'gb' + ' ' + storage + 'gb'
        search_requests.append(v)

        v = model2 + ' ' + ram + '/' + storage
        search_requests.append(v)

        v = model2 + ' ' + ram + ' ' + storage
        search_requests.append(v)

        v = brand + ' ' + model2 + ' ' + storage
        search_requests.append(v)

        v = model2 + ' ' + storage
        search_requests.append(v)

        return search_requests

    @staticmethod
    def _soup(url):
        r = MyPerfectRequest.Get(use_proxy=True, desktop_headers=True)
        soup = r.soup(url)
        return soup

    @staticmethod
    def _find_next_page(soup):
        try:
            next_page = soup.find('a', class_='_paginator_next_button').get('href')
        except:
            next_page = False

        return next_page

    @staticmethod
    def _get_title_and_price(soup):
        try:
            ads = soup.find_all('li', class_="product_item")
        except:
            ads = []

        result = []

        for ad in ads:
            try:
                title = ad.find('div', class_="product_item__title").text
                price = ad.find('div', class_="product_item__description").find('div').text
                price = re.sub("[^0-9]", "", price)
                result.append({title: price})
            except:
                continue

        return result

    def _title_sorting(self, data):
        result = {}

        for d in data:
            title = list(d.keys())[0].lower()
            price = list(d.values())[0]

            for each in self.search_requests:

                search = re.search(each, title)
                if search:
                    if not self.nfc:
                        search_nfc = re.search('nfc', title)
                        if not search_nfc:
                            try:
                                val = result[price]
                            except:
                                val = 0
                            result[price] = val + 1
                    else:
                        try:
                            val = result[price]
                        except:
                            val = 0
                        result[price] = val + 1

        sorted_result = {}

        for w in sorted(result, key=result.get, reverse=True):
            sorted_result[w] = result[w]

        return sorted_result

    def _price_sorting(self, sorted_data):
        try:
            max_value = max(list(sorted_data.values()))
        except:
            return False

        price_list = []
        top_price_list = []

        for d in sorted_data:
            key = d
            val = sorted_data[key]
            if not key or not val:
                continue
            if val == max_value or val == (max_value - 1):
                top_price_list.append(int(key))
                price_list.append(int(key))
            else:
                price_list.append(int(key))

        max_price = max(price_list)
        min_price = min(price_list)
        middle_price = mean(top_price_list)
        middle_price = round(middle_price / 500) * 500

        result = {'max_price_youla': max_price, 'min_price_youla': min_price,
                  'mid_price_youla': middle_price, 'url_youla': self.link}

        return result

    def _data_sorting(self, data):
        # data = [{title: price}]
        sorted_data = self._title_sorting(data)
        if sorted_data:
            sorted_result = self._price_sorting(sorted_data)
        else:
            sorted_result = {}

        return sorted_result

    def data_mining(self):
        url = self.link

        titles_prices_list = []

        while True:
            soup = self._soup(url)
            new_titles_prices_list = self._get_title_and_price(soup)
            titles_prices_list = titles_prices_list + new_titles_prices_list
            new_url = self._find_next_page(soup)
            if new_url:
                url = new_url
                continue
            else:
                break

        sorted_result = self._data_sorting(titles_prices_list)
        if not sorted_result:
            sorted_result = {'url_youla': self.link}

        return sorted_result


class Pda:

    def __init__(self):
        self._domain = 'https://4pda.ru/devdb/'
        self.__db_init()

    @staticmethod
    def __db_init():
        db = Pda_db.pda_db
        with db:
            db.create_tables([Pda_db.CategoriesLinksPda, Pda_db.BrandsLinksPda,
                              Pda_db.SmartphonesLinksPda, Pda_db.SmartphoneSpecificationsPda])

    @staticmethod
    def _categories_link_parsing(soup):
        # collect links of all categories on the main page
        db = Pda_db.CategoriesLinksPda
        today = date.today().strftime("%d.%m.%Y")

        try:
            category_block_list = soup.find('div', class_='types-list').find_all('div', class_='type-row')
        except:
            category_block_list = []

        for category in category_block_list:
            try:
                title = category.find('div', class_='title-text').find('h2').text
                href = category.find('div', class_='title-text').find('a').get('href')
                link = 'https:' + href + '/all'
            except:
                continue

            if title and link:
                try:
                    link_in_db = db.get(db.link == link)
                except:
                    link_in_db = ''

                if link_in_db:
                    continue
                else:
                    db.create(category=title, link=link, updated=today)

    @staticmethod
    def _get_brand_name_brands_links_parsing(title):
        try:
            title_split = title.split(' (')
            brand_name = title_split[0]
        except:
            brand_name = ''

        return brand_name

    def _brands_links_parsing(self, soup, category_name):
        # collect links of all brands in a given category
        today = date.today().strftime("%d.%m.%Y")
        db = Pda_db.BrandsLinksPda

        try:
            blocks_list = soup.find_all('ul', class_='word-list')
        except:
            blocks_list = []

        for block in blocks_list:
            try:
                brands_list = block.find_all('li')
            except:
                brands_list = []

            for brand in brands_list:
                try:
                    a = brand.find('a')
                    title = a.text
                    href = a.get('href')
                except:
                    continue

                link = 'https:' + href.replace('/all', '') + '/all'

                try:
                    is_double = db.select().where(db.link == link)
                except:
                    is_double = ''

                if is_double:
                    continue

                brand_name = self._get_brand_name_brands_links_parsing(title)

                if link and brand_name:
                    db.create(category=category_name, brand=brand_name, link=link, updated=today)
                else:
                    continue

    @staticmethod
    def _models_links_parsing(soup, brand_name):
        # collect link and image for each model in a given brand
        db = Pda_db.SmartphonesLinksPda

        try:
            models_list = soup.find_all('div', class_='box-holder')
        except:
            models_list = []

        for model in models_list:
            try:
                img = model.find('img')
                img_href = img.get('src')
                name = model.find('div', class_='name').find('a')
                model_name = name.text
                model_href = name.get('href')
            except:
                continue

            its_ipod = re.search(r'\bipod\b', model_name.lower())
            if its_ipod:
                continue

            img_link = 'https:' + img_href
            model_link = 'https:' + model_href

            try:
                is_double = db.select().where(db.link == model_link)
            except:
                is_double = ''

            if is_double:
                continue

            db.create(brand=brand_name, model=model_name, link=model_link, img=img_link)

    @staticmethod
    def _specifications_parsing_main(specifications_list):
        result = {}
        for row in specifications_list:
            try:
                row_title = row.find('dt').text.lower()
                row_value = row.find('dd').text
            except:
                continue

            its_brand = re.search(r'\bпроизводитель\b', row_title)
            if its_brand:
                try:
                    brand = row_value.lower()
                except:
                    continue
                result['brand'] = brand
                continue

            its_model = re.search(r'\bмодель\b', row_title)
            if its_model:
                try:
                    model = row_value.lower()
                except:
                    continue
                result['model'] = model
                continue

            its_release = re.search(r'\bгод\b', row_title)
            if its_release:
                try:
                    release = re.sub("[^0-9]", "", row_value)
                except:
                    continue
                result['release'] = str(release)
                continue

            its_os = re.search(r'\bсистема\b', row_title)
            if its_os:
                result['os'] = row_value
                continue

            its_battery = re.search(r'\bаккум\b', row_title)
            if its_battery:
                try:
                    battery = re.sub("[^0-9]", "", row_value)
                except:
                    continue
                result['battery'] = str(battery)
                continue
        return result

    @staticmethod
    def _specifications_parsing_dimensions(specifications_list):
        result = {}

        for row in specifications_list:
            try:
                row_title = row.find('dt').text.lower()
                row_value = row.find('dd').text
            except:
                continue

            its_dimensions = re.search(r'\bгабариты\b', row_title)
            if its_dimensions:
                result['dimensions'] = row_value
                continue

            its_weight = re.search(r'\bвес\b', row_title)
            if its_weight:
                try:
                    weight = re.sub("[^0-9]", "", row_value)
                except:
                    continue
                result['weight'] = str(weight)
                continue


        return result

    @staticmethod
    def _specifications_parsing_cpu(specifications_list):
        result = {}

        for row in specifications_list:
            try:
                row_title = row.find('dt').text.lower()
                row_value = row.find('dd').text
            except:
                continue

            its_cpu = re.search(r'\bпроцессор\b', row_title)
            if its_cpu:
                result['cpu'] = row_value
                continue

            its_core_speed = re.search(r'\bвес\b', row_title)
            if its_core_speed:
                try:
                    core_speed = re.sub("[^0-9]", "", row_value)
                except:
                    continue
                result['core_speed'] = str(core_speed)
                continue

        return result

    @staticmethod
    def _specifications_parsing_storage(specifications_list):
        pass

    @staticmethod
    def _specifications_parsing_display(specifications_list):
        result = {}

        for row in specifications_list:
            try:
                row_title = row.find('dt').text.lower()
                row_value = row.find('dd').text
            except:
                continue

            its_display = re.search(r'\bэкран\b', row_title)
            if its_display:
                try:
                    display = re.sub("[^0-9,.]", "", row_value)
                except:
                    continue
                result['display'] = str(display)
                continue

        return result

    def _models_specifications_parsing(self, soup, model_img):
        # collect data specification smartphone
        ekatalog_db = Smartphones_db.Smartphones
        db = Pda_db.SmartphoneSpecificationsPda
        result = {'img': model_img}

        try:
            specifications_blocks = soup.find_all('div', class_='specifications-list')
        except:
            specifications_blocks = []

        for block in specifications_blocks:
            try:
                title = block.find('h3', class_='specifications-title').text.lower()
            except:
                continue

            try:
                specifications_list = block.find_all('dl', class_='specifications-row')
            except:
                continue

            its_main = re.search(r'\bобщее\b', title)
            if its_main:
                main_block = self._specifications_parsing_main(specifications_list)
                result = {**result, **main_block}
                continue

            its_dimensions = re.search(r'\bразмеры\b', title)
            if its_dimensions:
                dimensions_block = self._specifications_parsing_dimensions(specifications_list)
                result = {**result, **dimensions_block}
                continue

            its_cpu = re.search(r'\bпроцессор\b', title)
            if its_cpu:
                cpu_block = self._specifications_parsing_cpu(specifications_list)
                result = {**result, **cpu_block}
                continue

            its_storage = re.search(r'\bпамять\b', title)
            if its_storage:
                storage_block = self._specifications_parsing_storage(specifications_list)
                continue

            its_display = re.search(r'\bмультимедиа\b', title)
            if its_display:
                display = self._specifications_parsing_display(specifications_list)
                result = {**result, **display}
                continue



        try:
            double = db.select().where() # TODO
        except:
            double = ''

        if not double:
            db.insert_many(result).execute()

    def total_parsing(self):
        # start a general collection or update of all data from the 4pda.ru/devdb/
        url = self._domain
        r = MyPerfectRequest.Get()
        soup = r.soup(url)

        self._categories_link_parsing(soup)

        try:
            categories = Pda_db.CategoriesLinksPda.select()
        except:
            categories = []

        for category in categories:
            try:
                title = category.category
                link = category.link
            except:
                continue
            soup = r.soup(link)
            self._brands_links_parsing(soup, title)

        try:
            smartphones_brands = Pda_db.BrandsLinksPda.select().where(Pda_db.BrandsLinksPda.category == 'Телефоны')
        except:
            smartphones_brands = []

        for brand in smartphones_brands:
            try:
                brand_name = brand.brand
                link = brand.link
            except:
                continue

            if not brand_name or not link:
                continue

            soup = r.soup(link)
            self._models_links_parsing(soup, brand_name)


'''
Если озу/память несколько, то передавать лист диктов
после передачи для каждого дикта создать свою модель, добавив остальные характеристики

NFC брать из бд екаталога, если нет, тогда False
В самую последнюю очередь и для кадой модели, если их несколько

в самом конце добавить в словарь через перебор листа диктов, даже если он будет один
'''