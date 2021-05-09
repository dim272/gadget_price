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
                    db.create(model=model, link=link)
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
    def _release_parsing(soup):
        release = None
        try:
            release_block = soup.find('div', class_='m-c-f1')
            release_part = release_block.find_all('span')
        except:
            release_part = ''

        if not release_part:
            try:
                release_block = soup.find('div', class_='m-c-f1')
                release_part = release_block.find_all('a')
            except:
                release_part = ''

        if release_part:
            for i in release_part:
                its_release = re.search(r'\bгод\b', i.text)
                if its_release:
                    release = re.sub("[^0-9]", "", i.text)
                    break

        return release

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
            except:
                shop_name = shop.find('h3').parent.next_sibling.find('a').text
            else:
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

        spec_dict = {'brand': brand, 'model': model}

        specifications = soup.find('div', class_='m-c-f2').select('.m-s-f3')

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

        in_stock = self._is_in_stock(soup)
        spec_dict['in_stock'] = bool(in_stock)

        price_dict = {}

        if in_stock:
            new_url = self._more_button_finder(soup)
            if new_url:
                soup = r.soup(new_url)
                price_dict = self._price_parsing(soup)

        final_dict = {**spec_dict, **price_dict}

        Smartphones_db.Smartphones.insert_many(final_dict).execute()

