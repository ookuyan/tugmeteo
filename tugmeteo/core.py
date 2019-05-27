#!/usr/bin/env python

__all__ = ['TugMeteo']

import requests
from bs4 import BeautifulSoup


class TugMeteo(object):

    def __init__(self):
        super(TugMeteo, self).__init__()

        self.telescope = 'all'
        self.telescopes = ['all', 'RTT150', 'T100', 'T60']

        self.telescopes_meteo_pages = {
            'RTT150': 'http://193.140.96.48'
            '/wxrss.xml',
            'T100': 'http://t100meteo.tug.tubitak.gov.tr/'
            'index.html/wxrss.xml',
            'T60': 'http://t60meteo.tug.tubitak.gov.tr/index.html/'}

        self.rtt150_last_meteo = {'Date': [0., ''],
                                  'Time': [0., ''],
                                  'Temperature': [0., ''],
                                  'Wind Chill': [0., ''],
                                  'Heat Index': [0., ''],
                                  'Humidity': [0., ''],
                                  'Dewpoint': [0., ''],
                                  'Barometer': [0., ''],
                                  'Wind': [0., ''],
                                  'Wind Direction': [0., '']}

        self.t100_last_meteo = {'Date': [0., ''],
                                'Time': [0., ''],
                                'Temperature': [0., ''],
                                'Wind Chill': [0., ''],
                                'Heat Index': [0., ''],
                                'Humidity': [0., ''],
                                'Dewpoint': [0., ''],
                                'Barometer': [0., ''],
                                'Wind': [0., ''],
                                'Wind Direction': [0., ''],
                                'Rain Today': [0., ''],
                                'Rain Rate': [0., '']}

        self.t60_last_meteo = {'Date': [0., ''],
                               'Time': [0., ''],
                               'Temperature': [0., ''],
                               'Wind Chill': [0., ''],
                               'Humidity': [0., ''],
                               'Dewpoint': [0., ''],
                               'Barometer': [0., ''],
                               'Wind': [0., ''],
                               'Wind Direction': [0., '']}

        self.last_meteos = {'RTT150': self.rtt150_last_meteo,
                            'T100': self.t100_last_meteo,
                            'T60': self.t60_last_meteo}

    def get_meteo_page(self, telescope='RTT150'):
        for tel, meteo_page in self.telescopes_meteo_pages.items():
            if tel == telescope:
                try:
                    respond = requests.get(meteo_page)
                except requests.exceptions.RequestException as exp:
                    print(exp)
                    continue

                if telescope == 'T60':
                    return respond.text
                else:
                    return respond.text.split('\n')

        return None

    def parse_meteo(self, html=None, telescope='RTT150'):
        if html is None:
            return False

        last_meteo = self.last_meteos[telescope]

        if telescope in ['RTT150', 'T100']:
            d = html[22].strip().split('>')[1].split('<')[0].split('-')
            last_meteo['Date'][0] = d[0].strip()
            last_meteo['Date'][1] = 'date'
            last_meteo['Time'][0] = d[1].strip()
            last_meteo['Time'][1] = 'time'
        elif telescope == 'T60':
            soup = BeautifulSoup(html, 'html.parser')
            row = soup.findAll('font', {'color': 'F8D23F', 'size': '4'})[0]
            date_time = row.findAll('font')[0].text.strip().split(',')

            time = date_time[0]
            date = date_time[1].strip()

            last_meteo['Date'][0] = date
            last_meteo['Date'][1] = 'date'
            last_meteo['Time'][0] = time
            last_meteo['Time'][1] = 'time'

            for row in soup.findAll('strong'):
                data = row.text.split('=')

                if row.text.find('HUMIDITY') == 0:
                    last_meteo['Humidity'][0] = data[1].strip()
                    last_meteo['Humidity'][1] = '%'

                if row.text.find('PRESSURE') == 0:
                    last_meteo['Barometer'][0] = data[1].strip()
                    last_meteo['Barometer'][1] = 'mb'

                if row.text.find('WINDSPEED') == 0:
                    last_meteo['Wind'][0] = data[1].strip()
                    last_meteo['Wind'][1] = 'km/h'

                if row.text.find('WINDDIR') == 0:
                    last_meteo['Wind Direction'][0] = data[1].strip()
                    last_meteo['Wind Direction'][1] = 'Deg'

                if row.text.find('Wind Chill') == 0:
                    last_meteo['Wind Chill'][0] = data[1].strip()
                    last_meteo['Wind Chill'][1] = 'C'

                if row.text.find('Dew Point') == 0:
                    last_meteo['Dewpoint'][0] = data[1].strip()
                    last_meteo['Dewpoint'][1] = 'C'

                if row.text.find('TEMPERATURE') == 0:
                    last_meteo['Temperature'][0] = data[1].strip()
                    last_meteo['Temperature'][1] = 'C'

            return True
        else:
            return False

        if telescope == 'RTT150':
            rows = html[27:34]
        elif telescope == 'T100':
            rows = html[25:34]
        else:
            return False

        for row in rows:
            row = row.strip().split('<br>')[0].split(': ')
            if row[0] == 'Date':
                continue

            if telescope == 'RTT150':
                last_meteo[row[0]][0] = row[1].split()[0]

                if row[0] == 'Barometer':
                    unit = row[1].split()
                    if len(unit) == 3:
                        last_meteo['Barometer'][1] = unit[1] + ' ' + unit[2]
                    else:
                        last_meteo['Barometer'][1] = unit[1]
                    continue
                elif row[0] == 'Wind':
                    unit = row[1].split()
                    last_meteo['Wind'][0] = unit[2]
                    last_meteo['Wind'][1] = unit[3]
                    last_meteo['Wind Direction'][0] = unit[0]
                    last_meteo['Wind Direction'][1] = 'direction'
                    continue
                else:
                    last_meteo[row[0]][1] = row[1].split()[1]

            elif telescope in ['T100']:
                if row[0] == 'Barometer':
                    unit = row[1].split()
                    last_meteo['Barometer'][0] = row[1].split()[0]
                    if len(unit) == 3:
                        last_meteo['Barometer'][1] = unit[1] + ' ' + unit[2]
                    else:
                        last_meteo['Barometer'][1] = unit[1]
                    continue
                elif row[0] == 'Temp':
                    last_meteo['Temperature'][0] = row[1].split()[0]
                    last_meteo['Temperature'][1] = row[1].split()[1]
                    continue
                elif row[0] == 'Wind':
                    unit = row[1].split()
                    last_meteo[row[0]][0] = unit[2]
                    last_meteo[row[0]][1] = unit[3]
                    last_meteo['Wind Direction'][0] = unit[0]
                    last_meteo['Wind Direction'][1] = 'direction'
                    continue
                else:
                    last_meteo[row[0]][0] = row[1].split()[0]
                    last_meteo[row[0]][1] = row[1].split()[1]
            else:
                return False

        return True

    def update(self, telescope='all'):
        if telescope not in self.telescopes:
            return False

        self.telescope = telescope

        ctrl = {'all': False, 'RTT150': False, 'T100': False, 'T60': False}

        if telescope in ['all', 'RTT150']:
            rtt150_page = self.get_meteo_page('RTT150')
            ctrl[telescope] = self.parse_meteo(rtt150_page, 'RTT150')

            if telescope != 'all':
                return ctrl

        if telescope in ['all', 'T100']:
            t100_page = self.get_meteo_page('T100')
            ctrl[telescope] = self.parse_meteo(t100_page, 'T100')

            if telescope != 'all':
                return ctrl

        if telescope in ['all', 'T60']:
            t60_page = self.get_meteo_page('T60')
            ctrl[telescope] = self.parse_meteo(t60_page, 'T60')

            if telescope != 'all':
                return ctrl

        if telescope == 'all':
            for tel in self.telescopes:
                ctrl[tel] = True

        return ctrl

    def get_meteo(self, telescope, meteo='Temperature'):
        if telescope not in self.telescopes:
            return False

        if self.telescope != 'all' and (telescope in self.telescope[1:]):
            return False

        if telescope == 'all' and self.telescope == 'all':
            res = dict()

            for tel in self.telescopes[1:]:
                res[tel] = self.last_meteos[tel][meteo]

            return res
        elif self.telescope == 'all' and telescope in self.telescopes[1:]:
            return self.last_meteos[telescope][meteo]
        elif self.telescope in self.telescopes[1:] and telescope == 'all':
            return self.last_meteos[self.telescope][meteo]
        else:
            return self.last_meteos[telescope][meteo]

    def get_temperature(self, telescope='all'):
        return self.get_meteo(telescope, 'Temperature')

    def get_humidity(self, telescope='all'):
        return self.get_meteo(telescope, 'Humidity')

    def get_pressure(self, telescope='all'):
        return self.get_meteo(telescope, 'Barometer')

    def get_wind_speed(self, telescope='all'):
        return self.get_meteo(telescope, 'Wind')

    def get_dew_point(self, telescope='all'):
        return self.get_meteo(telescope, 'Dewpoint')

    def get_wind_chill(self, telescope='all'):
        return self.get_meteo(telescope, 'Wind Chill')

    def get_date(self, telescope='all'):
        return self.get_meteo(telescope, 'Date')

    def get_time(self, telescope='all'):
        return self.get_meteo(telescope, 'Time')

    def show_meteo(self, telescope='all'):
        if telescope not in self.telescopes:
            return False

        if self.telescope != 'all' and telescope in self.telescope[1:]:
            return False

        if telescope == 'all' and self.telescope == 'all':
            for tel in self.telescopes[1:]:
                self.report(tel)
            return True
        elif self.telescope == 'all' and telescope in self.telescopes[1:]:
            self.report(telescope)
        elif self.telescope in self.telescopes[1:] and telescope == 'all':
            self.report(self.telescope)
        else:
            return False

    def report(self, telescope):
        print('Weather report from ' + telescope + ':')
        print('')

        for key, val in self.last_meteos[telescope].items():
            print(key + ': ' + str(val[0]) + ' [' + val[1] + ']')

        print("")
