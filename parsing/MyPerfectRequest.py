from random import choice
from time import sleep

import requests
from bs4 import BeautifulSoup

from parsing import MyPerfectProxy
from data import Proxy_db


class Get:
    def __init__(self, use_proxy=False, desktop_headers=False, android_headers=False, ios_headers=False):
        self._use_proxy = use_proxy
        self._desktop_h = desktop_headers
        self._android_h = android_headers
        self._ios_h = ios_headers

    @staticmethod
    def _random_headers(file_name):
        with open(file_name, 'r') as f:
            lines = f.readlines()
            random_line = choice(lines).replace('\n', '').replace('"', '')
            headers = {'User-Agent': random_line}
            return headers

    def _headers(self):
        desktop_headers = 'parsing/headers.csv'
        android_headers = 'parsing/headers_android.csv'
        iOS_headers = 'parsing/headers_iOS.csv'

        headers = ''

        if self._android_h or self._ios_h:
            if self._android_h and self._ios_h:
                random_ = choice([0, 1])
                if random_:
                    headers = self._random_headers(android_headers)
                else:
                    headers = self._random_headers(iOS_headers)

            elif self._android_h:
                headers = self._random_headers(android_headers)

            elif self._ios_h:
                headers = self._random_headers(iOS_headers)
        else:
            headers = self._random_headers(desktop_headers)

        return headers

    @staticmethod
    def _proxy():
        p = MyPerfectProxy.Get()
        proxy_list = p.new_list()
        return proxy_list

    def proxy_check(self, proxy, url):
        headers = self._headers()
        try:
            req = requests.get(url, headers=headers, proxies=proxy, timeout=7)
        except:
            req = ''

        return req

    def _request_with_proxy(self, url):
        p = MyPerfectProxy.Get()
        req = ''
        while True:
            print('Infinity request with proxy')
            proxy_db = Proxy_db.ProxyList.select()
            if not proxy_db:
                print('Dont find proxies in DB')
                p.new_list()
                continue
            print('I find proxies in DB. Lets check it')
            for i in proxy_db:
                schema = i.schema
                ip = i.proxy
                proxy = {schema: ip}
                print('Start check:', proxy)
                req = self.proxy_check(proxy, url)
                if req:
                    print('Proxy is cool:', req)
                    break
                else:
                    print('Proxy not cool:', req, 'Delete them!')
                    Proxy_db.ProxyList.delete().where(Proxy_db.ProxyList.proxy == ip).execute()
                    continue
            if req:
                print('We have the req, now we must the leave infinity cycle')
                break

            print('Proxy is ending, we need new list. Req is:', req)

        print('Yes! We leave them with req!!!! Return the req:', req)
        return req

    def request(self, url):
        if self._use_proxy:
            req = self._request_with_proxy(url)
        else:
            headers = self._headers()
            req = requests.get(url, headers=headers, timeout=3)

        return req

    def soup(self, url):
        r = self.request(url)
        soup = BeautifulSoup(r.text, 'lxml')
        return soup

    def manual_request_and_soup(self, url, proxy):
        headers = self._headers()
        req = requests.get(url, headers=headers, proxies=proxy, timeout=5)
        soup = BeautifulSoup(req.text, 'lxml')

        return soup