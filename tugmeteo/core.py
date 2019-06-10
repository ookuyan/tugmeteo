#!/usr/bin/env python

__all__ = ['TugMeteo']

import requests

from .helper import get_current_time_stamp, parse_meteo_page,\
    generate_meteo_archive_urls, parse_meteo_archive, concat_meteo_archive


class TugMeteo(object):

    def __init__(self, telescope='all'):
        """
        TugMeteo

        TÜBİTAK National Observatory Meteorology Library

        Parameters
        ----------
        telescope : str
            Telescope name.
            'telescope' must be one of 'RTT150', 'T100', 'T60' or 'all'.
            Default value is 'all'.

        Methods
        -------
        get_meteo_archives(telescope='RTT150', start_date='', end_date='',
                           date_format='%Y-%m-%d')
            Gets meteorology archive from database with 5 min interval.

        get_last_meteo(telescope='all')
            Return current all meteorological data.

        get_temperature(telescope='all')
            Returns current temperature.
            Unit is Celsius [C].

        get_dome_temperature(telescope='all')
            Returns current dome temperature.
            Unit is Celsius [C].

        get_humidity(telescope='all')
            Returns current humidity.
            Unit is RH [%].

        get_dome_humidity(telescope='all')
            Returns current dome humidity.
            Unit is RH [%].

        get_pressure(telescope='all')
            Returns current pressure.
            Unit is millibar [mb].

        get_wind_speed(telescope='all')
            Returns current wind speed.
            Unit is km/h.

        get_wind_chill(telescope='all')
            Returns current wind chill.
            Unit is Celsius [C].

        get_wind_direction(telescope='all')
            Returns current wind direction (azimuth -> from North).
            Unit is Degree.

        get_dew_point(telescope='all')
            Returns current dew point.
            Unit is Celsius [C].

        get_cumulus_base(telescope='all')
            Returns current cumulus cloud base.
            Unit is meter [m].

        get_rain(telescope='all')
            Returns current rain precipitation.
            Unit is mm/h.

        get_uv_index(telescope='all')
            Returns current uv index.
            Unit is index.

        get_solar_radiation(telescope='all')
            Returns current solar radiation.
            Unit is W / m^2.

        get_air_density(telescope='all')
            Returns current air density.
            Unit is kg / m^3.

        Examples
        --------
        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> data = met.get_last_meteo('RTT150')
        >>> print(data)
        {
            'timestamp': '2019-05-31T23:36:06',
            'telescope': 'RTT150',
            'Temperature': 13.0,
            'Dome Temperature': 15.3,
            'Coude Temperature': 13.0,
            'Humidity': 51.0,
            'Dome Humidity': 48.0,
            'Coude Humidity': 57.0,
            'Barometer': 757.6,
            'Wind': 13.0,
            'Wind Chill': 13.0,
            'Dewpoint': 3.1,
            'High Temperature': 17.2,
            'Low Temperature': 11.7,
            'High Humidity': 54.0,
            'Low Humidity': 32.0,
            'High Barometer': 759.7,
            'Low Barometer': 757.0,
            'High Wind': 37.0,
            'Est. Cumulus Base': 1239.0
        }
        >>>
        >>> p = met.get_pressure('T60')
        >>> print(p)
        {'timestamp': '2019-05-31T23:37:27', 'info': 'Pressure', 'T60': 758.1}
        >>>
        >>> table = met.get_meteo_archives(start_date='2019-02-10',
                                           end_date='2019-05-31')
        """

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
        """
        Internal using only.
        """

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
        """
        Internal using only.
        """

        page = self._get_meteo_page(telescope)

        if page is not None:
            last_meteo = parse_meteo_page(page, telescope)
            self._last_meteos[telescope] = last_meteo

            return True

        self._last_meteos[telescope] = None

        return False

    def _get_meteo_info(self, telescope, info_keywords, key):
        """
        Internal using only.
        """

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
            If None, return today's archive.

        end_date : str
            End date of the archive.
            It must be in the format specified by 'date_format'.

            If 'start_date' and 'end_date' are empty,
                return today's archive.

            If 'start_date' is not empty and 'end_date' is empty,
                returns archive between 'start_date' and today.

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
        >>> # Get today's archive (Default telescope is 'RTT150').
        >>> t = met.get_meteo_archives()
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
        """
        Return current all meteorological data.

        Parameters
        ----------
        telescope : str
            Telescope name.
            'telescope' must be one of 'RTT150', 'T100', 'T60' or 'all'.
            Default value is 'all'.

        Returns
        -------
        Type of 'dict'

        Examples
        --------

        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> data = met.get_last_meteo('RTT150')
        >>> print(data)
        {
            'timestamp': '2019-05-31T22:55:33',
            'telescope': 'RTT150',
            'Temperature': 13.8,
            'Dome Temperature': 14.7,
            'Coude Temperature': 13.0,
            'Humidity': 43.0,
            'Dome Humidity': 42.0,
            'Coude Humidity': 57.0,
            'Barometer': 757.7,
            'Wind': 10.0,
            'Wind Chill': 13.8,
            'Dewpoint': 1.5,
            'High Temperature': 17.2,
            'Low Temperature': 11.7,
            'High Humidity': 54.0,
            'Low Humidity': 32.0,
            'High Barometer': 759.7,
            'Low Barometer': 757.0,
            'High Wind': 37.0,
            'Est. Cumulus Base': 1547.0
        }
        """

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
        """
        Returns current temperature.
        Unit is Celsius [C].

        Parameters
        ----------
        telescope : str
            Telescope name.
            'telescope' must be one of 'RTT150', 'T100', 'T60' or 'all'.
            Default value is 'all'.

        Returns
        -------
        type of 'dict'
            Temperature value(s)

        Examples
        --------

        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> t = met.get_temperature('all')
        >>> print(t)
        {
            'timestamp': '2019-05-31T22:54:30',
            'info': 'Temperature',
            'RTT150': 13.9,
            'T100': 13.5,
            'T60': 13.8
        }
        """

        info_keywords = {
            'RTT150': 'Temperature',
            'T100': 'TEMPERATURE',
            'T60': 'TEMPERATURE'}

        return self._get_meteo_info(telescope, info_keywords, 'Temperature')

    def get_dome_temperature(self, telescope='all'):
        """
        Returns current dome temperature.
        Unit is Celsius [C].

        Parameters
        ----------
        telescope : str
            Telescope name.
            'telescope' must be one of 'RTT150', 'T100', 'T60' or 'all'.
            Default value is 'all'.

        Returns
        -------
        type of 'dict'
            Dome temperature value(s)

        Examples
        --------

        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> t = met.get_dome_temperature('all')
        >>> print(t)
        {
            'timestamp': '2019-05-31T22:57:15',
            'info': 'Dome Temperature',
            'RTT150': 14.7,
            'T100': None,
            'T60': 17.2
        }
        """

        info_keywords = {
            'RTT150': 'Dome Temperature',
            'T100': None,
            'T60': 'Inside Temperature'}

        return self._get_meteo_info(telescope, info_keywords,
                                    'Dome Temperature')

    def get_humidity(self, telescope='all'):
        """
        Returns current humidity.
        Unit is RH [%].

        Parameters
        ----------
        telescope : str
            Telescope name.
            'telescope' must be one of 'RTT150', 'T100', 'T60' or 'all'.
            Default value is 'all'.

        Returns
        -------
        type of 'dict'
            Humidity value(s)

        Examples
        --------

        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> t = met.get_humidity('all')
        >>> print(t)
        {
            'timestamp': '2019-05-31T22:58:18',
            'info': 'Humidity',
            'RTT150': 44.0,
            'T100': 43.0,
            'T60': 42.0
        }
        """

        info_keywords = {
            'RTT150': 'Humidity',
            'T100': 'HUMIDITY',
            'T60': 'HUMIDITY'}

        return self._get_meteo_info(telescope, info_keywords, 'Humidity')

    def get_dome_humidity(self, telescope='all'):
        """
        Returns current dome humidity.
        Unit is RH [%].

        Parameters
        ----------
        telescope : str
            Telescope name.
            'telescope' must be one of 'RTT150', 'T100', 'T60' or 'all'.
            Default value is 'all'.

        Returns
        -------
        type of 'dict'
            Dome humidity value(s)

        Examples
        --------

        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> t = met.get_dome_humidity('all')
        >>> print(t)
        {
            'timestamp': '2019-05-31T23:01:30',
            'info': 'Dome Humidity',
            'RTT150': 43.0,
            'T100': None,
            'T60': 36.0
        }
        """

        info_keywords = {
            'RTT150': 'Dome Humidity',
            'T100': None,
            'T60': 'Inside Humidity'}

        return self._get_meteo_info(telescope, info_keywords, 'Dome Humidity')

    def get_pressure(self, telescope='all'):
        """
        Returns current pressure.
        Unit is millibar [mb].

        Parameters
        ----------
        telescope : str
            Telescope name.
            'telescope' must be one of 'RTT150', 'T100', 'T60' or 'all'.
            Default value is 'all'.

        Returns
        -------
        type of 'dict'
            Pressure value(s)

        Examples
        --------

        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> t = met.get_pressure('all')
        >>> print(t)
        {
            'timestamp': '2019-05-31T23:04:42',
            'info': 'Pressure',
            'RTT150': 757.7,
            'T100': 755.8,
            'T60': 757.9
        }
        """

        info_keywords = {
            'RTT150': 'Barometer',
            'T100': 'PRESSURE',
            'T60': 'PRESSURE'}

        return self._get_meteo_info(telescope, info_keywords, 'Pressure')

    def get_wind_speed(self, telescope='all'):
        """
        Returns current wind speed.
        Unit is km/h.

        Parameters
        ----------
        telescope : str
            Telescope name.
            'telescope' must be one of 'RTT150', 'T100', 'T60' or 'all'.
            Default value is 'all'.

        Returns
        -------
        type of 'dict'
            Wind speed value(s)

        Examples
        --------

        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> t = met.get_wind_speed('all')
        >>> print(t)
        {
            'timestamp': '2019-05-31T23:07:08',
            'info': 'Wind Speed',
            'RTT150': 6.0,
            'T100': 24.1,
            'T60': 11.3
        }
        """

        info_keywords = {
            'RTT150': 'Wind',
            'T100': 'WINDSPEED',
            'T60': 'WINDSPEED'}

        return self._get_meteo_info(telescope, info_keywords, 'Wind Speed')

    def get_wind_chill(self, telescope='all'):
        """
        Returns current wind chill.
        Unit is Celsius [C].

        Parameters
        ----------
        telescope : str
            Telescope name.
            'telescope' must be one of 'RTT150', 'T100', 'T60' or 'all'.
            Default value is 'all'.

        Returns
        -------
        type of 'dict'
            Wind chill value(s)

        Examples
        --------

        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> t = met.get_wind_chill('all')
        >>> print(t)
        {
            'timestamp': '2019-05-31T23:09:06',
            'info': 'Wind Chill',
            'RTT150': 13.4,
            'T100': 13.1,
            'T60': 13.5
        }
        """

        info_keywords = {
            'RTT150': 'Wind Chill',
            'T100': 'Wind Chill',
            'T60': 'Wind Chill'}

        return self._get_meteo_info(telescope, info_keywords, 'Wind Chill')

    def get_wind_direction(self, telescope='all'):
        """
        Returns current wind direction (azimuth -> from North).
        Unit is Degree.

        Parameters
        ----------
        telescope : str
            Telescope name.
            'telescope' must be one of 'RTT150', 'T100', 'T60' or 'all'.
            Default value is 'all'.

        Returns
        -------
        type of 'dict'
            Wind chill value(s)

        Examples
        --------

        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> t = met.get_wind_direction('all')
        >>> print(t)
        {
            'timestamp': '2019-05-31T23:10:31',
            'info': 'Wind Direction',
            'RTT150': None,
            'T100': 59.0,
            'T60': 238.0
        }
        """

        info_keywords = {
            'RTT150': None,
            'T100': 'WINDDIR',
            'T60': 'WINDDIR'}

        return self._get_meteo_info(telescope, info_keywords, 'Wind Direction')

    def get_dew_point(self, telescope='all'):
        """
        Returns current dew point.
        Unit is Celsius [C].

        Parameters
        ----------
        telescope : str
            Telescope name.
            'telescope' must be one of 'RTT150', 'T100', 'T60' or 'all'.
            Default value is 'all'.

        Returns
        -------
        type of 'dict'
            Dew point value(s)

        Examples
        --------

        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> t = met.get_dew_point('all')
        >>> print(t)
        {
            'timestamp': '2019-05-31T23:12:02',
            'info': 'Dew Point',
            'RTT150': 2.0,
            'T100': 1.7,
            'T60': 1.7
        }
        """

        info_keywords = {
            'RTT150': 'Dewpoint',
            'T100': 'Dew Point',
            'T60': 'Dew Point'}

        return self._get_meteo_info(telescope, info_keywords, 'Dew Point')

    def get_cumulus_base(self, telescope='all'):
        """
        Returns current cumulus cloud base.
        Unit is meter [m].

        Parameters
        ----------
        telescope : str
            Telescope name.
            'telescope' must be one of 'RTT150', 'T100', 'T60' or 'all'.
            Default value is 'all'.

        Returns
        -------
        type of 'dict'
            Cumulus base value(s)

        Examples
        --------

        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> t = met.get_cumulus_base('all')
        >>> print(t)
        {
            'timestamp': '2019-05-31T23:13:19',
            'info': 'Est. Cumulus Base',
            'RTT150': 1387.0,
            'T100': 1383.0,
            'T60': 1463.0
        }
        """

        info_keywords = {
            'RTT150': 'Est. Cumulus Base',
            'T100': 'Est. Cumulus Base',
            'T60': 'Est. Cumulus Base'}

        return self._get_meteo_info(telescope, info_keywords,
                                    'Est. Cumulus Base')

    def get_rain(self, telescope='all'):
        """
        Returns current rain precipitation.
        Unit is mm/h.

        Parameters
        ----------
        telescope : str
            Telescope name.
            'telescope' must be one of 'RTT150', 'T100', 'T60' or 'all'.
            Default value is 'all'.

        Returns
        -------
        type of 'dict'
            Rain precipitation value(s)

        Examples
        --------

        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> t = met.get_rain('all')
        >>> print(t)
        {
            'timestamp': '2019-05-31T23:15:08',
            'info': 'Rain',
            'RTT150': None,
            'T100': 0.0,
            'T60': 0.0
        }
        """

        info_keywords = {
            'RTT150': None,
            'T100': 'RAIN',
            'T60': 'RAIN'}

        return self._get_meteo_info(telescope, info_keywords, 'Rain')

    def get_uv_index(self, telescope='all'):
        """
        Returns current uv index.
        Unit is index.

        Parameters
        ----------
        telescope : str
            Telescope name.
            'telescope' must be one of 'RTT150', 'T100', 'T60' or 'all'.
            Default value is 'all'.

        Returns
        -------
        type of 'dict'
            UV index value(s)

        Examples
        --------

        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> t = met.get_uv_index('all')
        >>> print(t)
        {
            'timestamp': '2019-05-31T23:16:08',
            'info': 'UV Index',
            'RTT150': None,
            'T100': 0.0,
            'T60': 0.0
        }
        """

        info_keywords = {
            'RTT150': None,
            'T100': 'UV',
            'T60': 'UV'}

        return self._get_meteo_info(telescope, info_keywords, 'UV Index')

    def get_solar_radiation(self, telescope='all'):
        """
        Returns current solar radiation.
        Unit is W / m^2.

        Parameters
        ----------
        telescope : str
            Telescope name.
            'telescope' must be one of 'RTT150', 'T100', 'T60' or 'all'.
            Default value is 'all'.

        Returns
        -------
        type of 'dict'
            Solar radiation value(s)

        Examples
        --------

        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> t = met.get_solar_radiation('all')
        >>> print(t)
        {
            'timestamp': '2019-05-31T23:17:40',
            'info': 'Solar Radiation',
            'RTT150': None,
            'T100': 0.0,
            'T60': 0.0
        }
        """

        info_keywords = {
            'RTT150': None,
            'T100': 'Solar Radiation',
            'T60': 'Solar Radiation'}

        return self._get_meteo_info(telescope, info_keywords,
                                    'Solar Radiation')

    def get_air_density(self, telescope='all'):
        """
        Returns current air density.
        Unit is kg / m^3.

        Parameters
        ----------
        telescope : str
            Telescope name.
            'telescope' must be one of 'RTT150', 'T100', 'T60' or 'all'.
            Default value is 'all'.

        Returns
        -------
        type of 'dict'
            Air density value(s)

        Examples
        --------

        >>> from tugmeteo import TugMeteo
        >>>
        >>> met = TugMeteo()
        >>>
        >>> t = met.get_air_density('all')
        >>> print(t)
        {
            'timestamp': '2019-05-31T23:18:41',
            'info': 'Air Density',
            'RTT150': None,
            'T100': 0.917,
            'T60': 0.918
        }
        """

        info_keywords = {
            'RTT150': None,
            'T100': 'Air Density',
            'T60': 'Air Density'}

        return self._get_meteo_info(telescope, info_keywords, 'Air Density')
