import re

from parsing import MyPerfectRequest
from data import Ekatalog_db, Smartphones_db


class Ekatalog():

    @staticmethod
    def main_page():
        request = MyPerfectRequest.Get(use_proxy=True, android_headers=True)
        url = 'https://www.e-katalog.ru/'
        soup = request.soup(url)
        cache = soup.find_all('div', class_='main_slide')

        for item in cache:
            a = item.find('a')
            section = a.text
            href = a['href'].replace('/', '')
            link = url + href
            print('Добавлям:', section, link)
            Ekatalog_db.HomePageLinks.create(section=section, link=link)

    @staticmethod
    def all_link_of_section(url):
        home = 'https://www.e-katalog.ru'
        request = MyPerfectRequest.Get(use_proxy=True, android_headers=True)
        soup = request.soup(url)
        a = soup.find('div', class_='all-link').find('a')
        href = a['href']
        link = home + href

        return link

    @staticmethod
    def find_next_page_link(soup):
        patern = 'https://www.e-katalog.ru'

        try:
            next_page = soup.find('a', id='pager_next')
            href = next_page.get('href')
            link = patern + href
        except:
            link = False

        return link

    @staticmethod
    def brands_links(url):
        pattern = 'https://www.e-katalog.ru'
        r = MyPerfectRequest.Get(use_proxy=True, android_headers=True)
        soup = r.soup(url)
        links = soup.find('div', class_='brands-list').find_all('a')

        for each in links:
            brand = each.text
            href = each.get('href') if 'list' in each.get('href') else ''
            if href:
                link = pattern + href
                Ekatalog_db.BrandsLinks.create(brand=brand, link=link)
            else:
                continue

    def smartphones_links(self, url):
        pattern = 'https://www.e-katalog.ru'
        r = MyPerfectRequest.Get(use_proxy=True, android_headers=True)
        db = Ekatalog_db.SmartphonesLinks
        while True:
            soup = r.soup(url)
            items = soup.find_all('a', class_='model-short-title')
            for item in items:
                href = item.get('href')
                link = pattern + href
                text_list = item.find_all('span')
                model_name = text_list[0].text
                try:
                    storage = text_list[1].text
                    model = model_name + ' ' + storage
                except:
                    model = model_name

                double = db.select().where(db.model == model)

                if not double:
                    print('Adding model:', model, link)
                    db.create(model=model, link=link)
                else:
                    print('Model already exist:', model)
                    continue

            next_page = self.find_next_page_link(soup)
            if next_page:
                print('Next page:', next_page)
                url = next_page
            else:
                print('Next false')
                break

    @staticmethod
    def _brand_name_finder(soup):
        script_list = soup.find('head').find_all('script')
        brand = ''
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
        title = soup.find('div', id='top-page-title').get('data-title')

        a = title.split('<span')
        b = a[0].strip().split(' ')

        brand_part_list = brand_name.split(' ')
        if len(brand_part_list) > 1:
            for brand_part in brand_part_list:
                b.remove(brand_part)
        else:
            b.remove(brand_name)

        model_name = ' '.join(b)
        return model_name

    @staticmethod
    def _display_parsing(each_spec):
        search_display = re.search(r'[:].{4}', each_spec.text).group()
        display = re.sub("[^0-9.]", "", search_display)
        return display

    @staticmethod
    def _storage_parsing(each_spec):
        search_storage = re.search(r'[:].{5}', each_spec.text).group()
        storage = re.sub("[^0-9.]", "", search_storage)
        return storage

    @staticmethod
    def _ram_parsing(each_spec):
        search_ram = re.search(r'[У].{4}', each_spec.text).group()
        ram = re.sub("[^0-9.]", "", search_ram)
        return ram

    @staticmethod
    def _num_cores_parsing(each_spec):
        try:
            search_core = re.search(r'[:].{4}', each_spec.text).group()
            num_cores = re.sub("[^0-9.]", "", search_core)
        except AttributeError:
            num_cores = ''
        return num_cores

    @staticmethod
    def _core_speed_parsing(each_spec):
        try:
            search_speed = re.search(r'[,].{4}', each_spec.text).group()
            core_speed = re.sub("[^0-9.]", "", search_speed)
        except AttributeError:
            core_speed = ''
        return core_speed

    @staticmethod
    def _battery_parsing(each_spec):
        search_battery = re.search(r'[:].{7}', each_spec.text).group()
        battery = re.sub("[^0-9.]", "", search_battery)
        return battery

    @staticmethod
    def _weight_parsing(each_spec):
        search_weight = re.search(r'[:].{5}', each_spec.text).group()
        weight = re.sub("[^0-9.]", "", search_weight)
        return weight

    @staticmethod
    def _release_parsing(soup):
        release_block = soup.select('div > div.m-c-f1.no-mobile > a.ib.no-u')
        release = None

        for each_release in release_block:
            its_release = re.search(r'\bгод\b', each_release.text)
            if its_release:
                release = re.sub("[^0-9]", "", each_release.text)
                break

        return release

    @staticmethod
    def _is_in_stock(soup):
        in_stock = True
        top_block = soup.find('div', class_='desc-short-prices')
        not_in_stock = top_block.select('.desc-not-avail')
        expected_on_sale = top_block.select('.or')

        if not_in_stock or expected_on_sale:
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
    def _price_parsing(soup):
        where_buy = soup.find('div', class_='where-buy-table')
        shops = where_buy[0].find_all("tr", {"class": True})

        # Магазины которые нас интересуют
        favorite_shops = ['mts.ru', 'svyaznoy.ru', 'citilink.ru', 'м.видео', 'megafon.ru', 'eldorado.ru',
                          'ozon.ru', 'sbermegamarket.ru']

        # Если магазин из списка, вынимаем название и стоимость
        for shop in shops:
            shop_name = shop.find("a", {'class': 'it-shop'}).text

            if shop_name.lower() not in favorite_shops:
                continue

            shop_name_dot_ru = re.search(r'\bru\b', shop_name)
            if shop_name_dot_ru:
                dict_key = 'price_' + shop_name.lower().replace('.ru', '')
            else:
                dict_key = 'price_mvideo'

            price_block = shop.select('.where-buy-price > a')
            price = re.sub("[^0-9]", "", price_block[0].text)

    def smartphone_specification(self, url):
        db = Smartphones_db.Smartphones

        r = MyPerfectRequest.Get(use_proxy=True, android_headers=True)
        soup = r.soup(url)

        brand = self._brand_name_finder(soup)
        model = self._model_name_finder(soup, brand)

        specifications = soup.find('div', class_='m-c-f2').select('.m-s-f3')

        for each_spec in specifications:

            its_display = re.search(r'\bЭкран\b', each_spec.text)
            if its_display:
                display = self._display_parsing(each_spec)
                continue

            its_storage = re.search(r'\bПамять\b', each_spec.text)
            if its_storage:
                storage = self._storage_parsing(each_spec)
                ram = self._ram_parsing(each_spec)
                continue

            its_cpu = re.search(r'\bПроцессор\b', each_spec.text)
            if its_cpu:
                num_cores = self._num_cores_parsing(each_spec)
                core_speed = self._core_speed_parsing(each_spec)
                continue

            its_battery = re.search(r'\bЕмкость батареи\b', each_spec.text)
            if its_battery:
                battery = self._battery_parsing(each_spec)
                continue

            its_weight = re.search(r'\bВес\b', each_spec.text)
            if its_weight:
                weight = self._weight_parsing(each_spec)
                continue

        db.create(brand=brand, model=model, display=display, storage=storage, ram=ram, num_cores=num_cores,
                  core_speed=core_speed, battery=battery, weight=weight)

        release = self._release_parsing(soup)
        if release:
            db.update({db.release: release}).where(db.model == model, db.storage == storage, db.ram == ram).execute()

        in_stock = self._is_in_stock(soup)
        db.update({db.in_stock: in_stock}).where(db.model == model, db.storage == storage, db.ram == ram).execute()

        if in_stock:
            new_url = self._more_button_finder(soup)
            if new_url:
                soup = r.soup(new_url)
                self._price_parsing(soup)
            else:
                pass
                # тут наверно нужна функция сбора цен, когда нет кнопки "ещё"

        # настроить парсинг и попробовать собрать результаты в дикт, вернуть его и вставить в базу разом
        # поправить cpu_num и core_speed
