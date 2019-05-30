#!/usr/bin/env python

__all__ = ['TugMeteo']

import requests
from datetime import datetime
from bs4 import BeautifulSoup


def get_current_time_stamp():
    t = datetime.now()
    return t.strftime('%Y-%m-%dT%H:%M%:%S')


def parse_meteo_page(html, telescope):
    last_meteo = dict()

    last_meteo['timestamp'] = get_current_time_stamp()

    soup = BeautifulSoup(html, 'html.parser')
    table = soup.findAll('table', {
        'cellspacing': '1', 'cellpadding': '0',
        'width': '100%', 'align': 'left'})[0]

    if telescope == 'RTT150':
        last_meteo['telescope'] = 'RTT150'

        keywords = list()

        for x in table.findAll('strong'):
            keywords.append(x.text.strip().replace(':', ''))

        for i, val in enumerate(table.findAll('b')):
            val = val.text.replace('\n', '').replace('\xa0', '').split(' ')

            if i != 7:
                last_meteo[keywords[i]] = float(val[0])
            else:
                last_meteo[keywords[i]] = float(val[-2])

        return last_meteo
    elif telescope == 'T100':
        last_meteo['telescope'] = 'T100'

        for x in table.findAll('strong'):
            x = x.text.split('=')

            keyword = x[0].strip()
            value = x[-1].strip()

            last_meteo[keyword] = float(value)

        for x in soup.findAll('b')[12:29][0::2]:
            x = x.text.split('=')

            keyword = x[0].strip()
            value = x[-1].strip()

            last_meteo[keyword] = float(value)

        return last_meteo
    else:
        last_meteo['telescope'] = 'T60'

        for x in table.findAll('strong'):
            x = x.text.split('=')

            keyword = x[0].strip()
            value = x[-1].strip()

            last_meteo[keyword] = float(value)

        for x in soup.findAll('b')[13:30][0::2]:
            x = x.text.split('=')

            keyword = x[0].strip()
            value = x[-1].strip()

            last_meteo[keyword] = float(value)

        return last_meteo


class TugMeteo(object):

    def __init__(self, telescope='all'):
        super(TugMeteo, self).__init__()

        self._telescope = telescope

        self._telescopes = ['RTT150', 'T100', 'T60']

        self._telescopes_meteo_pages = {
            'RTT150': 'http://rtt150meteo.tug.tubitak.gov.tr',
            'T100': 'http://t100meteo.tug.tubitak.gov.tr',
            'T60': 'http://t60meteo.tug.tubitak.gov.tr/index.html/'}

        self._last_meteos = {'RTT150': None, 'T100': None, 'T60': None}

    def _get_meteo_page(self, telescope):
        if telescope in self._telescopes:
            try:
                respond = requests.get(
                    self._telescopes_meteo_pages[telescope])
            except requests.exceptions.RequestException as exp:
                print(exp)
                return None

            return respond.text

        return None

    def _update(self, telescope):
        page = self._get_meteo_page(telescope)

        if page is not None:
            last_meteo = parse_meteo_page(page, telescope)
            self._last_meteos[telescope] = last_meteo

            return True

        self._last_meteos[telescope] = None

        return False

    def get_last_meteo(self, telescope='all'):
        if telescope == 'all':
            self._telescope = telescope

            for telescope in self._telescopes:
                self._update(telescope)

            return self._last_meteos

        if telescope in self._telescopes:
            self._telescope = telescope

            self._update(telescope)

            return self._last_meteos[telescope]

        return None

    def _get_meteo_info(self, telescope, info_keywords, key):
        info = dict()
        info['timestamp'] = get_current_time_stamp()
        info['info'] = key

        if self.get_last_meteo(telescope) is not None:
            if telescope == 'all':
                for tel in self._telescopes:
                    keyword = info_keywords[tel]
                    if keyword is not None:
                        info[tel] = self._last_meteos[tel][keyword]
                    else:
                        info[tel] = None
            else:
                keyword = info_keywords[telescope]
                if keyword is not None:
                    info[telescope] = self._last_meteos[telescope][keyword]
                else:
                    info[telescope] = None

            return info
        else:
            return None

    def get_temperature(self, telescope='all'):
        info_keywords = {
            'RTT150': 'Temperature',
            'T100': 'TEMPERATURE',
            'T60': 'TEMPERATURE'}

        return self._get_meteo_info(telescope, info_keywords, 'Temperature')

    def get_dome_temperature(self, telescope='all'):
        info_keywords = {
            'RTT150': 'Dome Temperature',
            'T100': None,
            'T60': 'Inside Temperature'}

        return self._get_meteo_info(telescope, info_keywords,
                                    'Dome Temperature')

    def get_humidity(self, telescope='all'):
        info_keywords = {
            'RTT150': 'Humidity',
            'T100': 'HUMIDITY',
            'T60': 'HUMIDITY'}

        return self._get_meteo_info(telescope, info_keywords, 'Humidity')

    def get_dome_humidity(self, telescope='all'):
        info_keywords = {
            'RTT150': 'Dome Humidity',
            'T100': None,
            'T60': 'Inside Humidity'}

        return self._get_meteo_info(telescope, info_keywords, 'Dome Humidity')

    def get_pressure(self, telescope='all'):
        info_keywords = {
            'RTT150': 'Barometer',
            'T100': 'PRESSURE',
            'T60': 'PRESSURE'}

        return self._get_meteo_info(telescope, info_keywords, 'Pressure')

    def get_wind_speed(self, telescope='all'):
        info_keywords = {
            'RTT150': 'Wind',
            'T100': 'WINDSPEED',
            'T60': 'WINDSPEED'}

        return self._get_meteo_info(telescope, info_keywords, 'Wind Speed')

    def get_wind_chill(self, telescope='all'):
        info_keywords = {
            'RTT150': 'Wind Chill',
            'T100': 'Wind Chill',
            'T60': 'Wind Chill'}

        return self._get_meteo_info(telescope, info_keywords, 'Wind Chill')

    def get_wind_direction(self, telescope='all'):
        info_keywords = {
            'RTT150': None,
            'T100': 'WINDDIR',
            'T60': 'WINDDIR'}

        return self._get_meteo_info(telescope, info_keywords, 'Wind Direction')

    def get_dew_point(self, telescope='all'):
        info_keywords = {
            'RTT150': 'Dewpoint',
            'T100': 'Dew Point',
            'T60': 'Dew Point'}

        return self._get_meteo_info(telescope, info_keywords, 'Dew Point')

    def get_cumulus_base(self, telescope='all'):
        info_keywords = {
            'RTT150': 'Est. Cumulus Base',
            'T100': 'Est. Cumulus Base',
            'T60': 'Est. Cumulus Base'}

        return self._get_meteo_info(telescope, info_keywords,
                                    'Est. Cumulus Base')

    def get_rain(self, telescope='all'):
        info_keywords = {
            'RTT150': None,
            'T100': 'RAIN',
            'T60': 'RAIN'}

        return self._get_meteo_info(telescope, info_keywords, 'Rain')

    def get_uv_index(self, telescope='all'):
        info_keywords = {
            'RTT150': None,
            'T100': 'UV',
            'T60': 'UV'}

        return self._get_meteo_info(telescope, info_keywords, 'UV Index')

    def get_solar_radiation(self, telescope='all'):
        info_keywords = {
            'RTT150': None,
            'T100': 'Solar Radiation',
            'T60': 'Solar Radiation'}

        return self._get_meteo_info(telescope, info_keywords,
                                    'Solar Radiation')

    def get_air_density(self, telescope='all'):
        info_keywords = {
            'RTT150': None,
            'T100': 'Air Density',
            'T60': 'Air Density'}

        return self._get_meteo_info(telescope, info_keywords, 'Air Density')
