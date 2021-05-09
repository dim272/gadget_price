from random import choice

import requests
from bs4 import BeautifulSoup

from data import Proxy_db

class Get:
    def __init__(self):
        self._soup = self._get_soup()

    @staticmethod
    def _get_soup():
        url = 'https://free-proxy-list.net/'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        return soup

    def new_list(self):
        proxy_list = []
        try:
            tr_list = self._soup.find('table', id='proxylisttable').find_all('tr')[1:21]
        except:
            tr_list = []
        db = Proxy_db.ProxyList()
        if tr_list:
            for tr in tr_list:
                td = tr.find_all('td')
                ip = td[0].text
                port = td[1].text
                schema = 'https' if 'yes' in td[6].text else 'http'
                proxy = ip + ':' + port
                db.create(schema=schema, proxy=proxy)

        return proxy_list

    def one_random(self):
        proxy_list = self.new_list()
        random_proxy = choice(proxy_list)

        return random_proxy

    @staticmethod
    def _check_proxy(proxy_list, url):
        valid_proxy_list = []

        for proxy in proxy_list:
            print('check proxy:', proxy)
            try:
                request = requests.get(url, proxies=proxy, timeout=5)
                print('OK - ', request.status_code)
                valid_proxy_list.append(proxy)
            except:
                print('False')
                continue

        return valid_proxy_list

    def checked_list(self, url):
        print('Checked list')
        proxy_list = self.new_list()
        checked_list = self._check_proxy(proxy_list, url)

        return checked_list
