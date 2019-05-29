#!/usr/bin/env python

__all__ = ['TugMeteo']

import requests
from bs4 import BeautifulSoup


class TugMeteo(object):

    def __init__(self):
        super(TugMeteo, self).__init__()

        self._telescopes = ['RTT150', 'T100', 'T60']

        self._telescopes_meteo_pages = {
            'RTT150': 'http://rtt150meteo.tug.tubitak.gov.tr',
            'T100': 'http://t100meteo.tug.tubitak.gov.tr',
            'T60': 'http://t60meteo.tug.tubitak.gov.tr/index.html/'}

        self._last_meteos = {'RTT150': None, 'T100': None, 'T60': None}

    def _get_meteo_page(self, telescope='RTT150'):
        if telescope in self._telescopes:
            try:
                respond = requests.get(
                    self._telescopes_meteo_pages[telescope])
            except requests.exceptions.RequestException as exp:
                print(exp)
                return None

            return respond.text

        return None

    def _parse_meteo(self, html=None, telescope='RTT150'):
        if telescope not in self._telescopes:
            return None

        if telescope == 'RTT150':
            last_meteo = dict()
            soup = BeautifulSoup(html, 'html.parser')

            table = soup.findAll('table', {
                'cellspacing': '1', 'cellpadding': '0',
                'width': '100%', 'align': 'left',
                'border': '1'})[0]

            keywords = list()
            for x in table.findAll('strong'):
                keywords.append(x.text.strip().replace(':', ''))

            for i, val in enumerate(table.findAll('b')):
                val = val.text.replace('\n', '').replace('\xa0', '').split(' ')

                if i != 7:
                    last_meteo[keywords[i]] = val[0]
                else:
                    last_meteo[keywords[i]] = val[-2]

            return last_meteo

    def update(self, telescope='RTT150'):
        if telescope not in self._telescopes:
            return False

        page = self._get_meteo_page(telescope)

        if page is not None:
            last_meteo = self._parse_meteo(page, telescope)
            self._last_meteos[telescope] = last_meteo

            return True

        return False

    def get_last_meteo(self, telescope='RTT150'):
        self.update(telescope)

        return self._last_meteos[telescope]
