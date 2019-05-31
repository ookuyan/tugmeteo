#!/usr/bin/env python

__all__ = ['TugMeteo']

import requests

from .helper import get_current_time_stamp, parse_meteo_page,\
    generate_meteo_archive_urls, parse_meteo_archive, concat_meteo_archive


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

        self._meteo_archives = {'RTT150': None, 'T100': None, 'T60': None}

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

    def get_meteo_archives(self, telescope='RTT150', start_date='', end_date='',
                           date_format='%Y-%m-%d'):
        """
        Gets meteorology archive from database with 5 min interval.

        Parameters
        ----------

        telescope : str
            The name of the meteorological station (telescope names).
            Default value is 'RTT150'.

        start_date : str
            Start date of the archive.
            It must be in the format specified by 'date_format'.
            If None, return today's archive url.

        end_date : str
            End date of the archive.
            It must be in the format specified by 'date_format'.
            If None, return today's archive url.

        date_format : str
            Date format for 'start_date' and 'end_date' parameters.

        Returns
        -------
        'pandas.DataFrame'
            Returned archive.

        Examples
        --------

        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> # Returns data from the archive for 7 days.
        >>> t = met.get_meteo_archives(telescope='T100',
                                       start_date='2017-05-31',
                                       end_date='2019-06-07')
        >>>
        >>> # Get today's archive.
        >>> t = met.get_meteo_archives(telescope='RTT150')
        """

        if not isinstance(telescope, str):
            raise TypeError("'telescope' should be a 'str' object.")

        if telescope not in self._telescopes:
            raise ValueError(
                "'telescope' must be one of 'RTT150', 'T100' or 'T60'.")

        if not isinstance(start_date, str):
            raise TypeError("'start_date' should be a 'str' object.")

        if not isinstance(end_date, str):
            raise TypeError("'end_date' should be a 'str' object.")

        urls = generate_meteo_archive_urls(telescope, start_date,
                                           end_date, date_format)

        if urls is None:
            return None

        raw_archives = list()
        for url in urls:
            r = requests.get(url)
            if not r.ok:
                continue

            raw_archives.append(r.text)

        tables = list()
        for raw_archive in raw_archives:
            table = parse_meteo_archive(raw_archive)
            tables.append(table)

        t = concat_meteo_archive(tables)

        self._meteo_archives[telescope] = t

        return t

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
