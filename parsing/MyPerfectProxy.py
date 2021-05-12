from random import choice

import requests
from bs4 import BeautifulSoup

from data.Proxy_db import *

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
        try:
            tr_list = self._soup.find('table', id='proxylisttable').find('tbody').find_all('tr')
        except:
            tr_list = []

        with proxy_db:
            proxy_db.create_tables([ProxyList])

        if tr_list:
            for tr in tr_list:
                td = tr.find_all('td')
                ip = td[0].text
                port = td[1].text
                schema = 'https' if 'yes' in td[6].text else 'http'
                proxy = ip + ':' + port
                ProxyList.create(schema=schema, proxy=proxy)

    def one_random(self):
        proxy_list = self.new_list()
        random_proxy = choice(proxy_list)

        return random_proxy

    @staticmethod
    def _check_proxy(proxy_list, url):
        valid_proxy_list = []

        for proxy in proxy_list:
            try:
                request = requests.get(url, proxies=proxy, timeout=5)
                valid_proxy_list.append(proxy)
            except:
                continue

        return valid_proxy_list

