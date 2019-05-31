#!/usr/bin/env python

from io import StringIO
from datetime import datetime, timedelta

from bs4 import BeautifulSoup

import numpy as np
import pandas as pd


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


def generate_meteo_archive_urls(telescope, start_date, end_date, date_format):
    if (start_date == '') or (end_date == ''):
        start_date = datetime.today()
        end_date = start_date + timedelta(days=1)
    else:
        try:
            start_date = datetime.strptime(start_date, date_format)
        except ValueError as error:
            raise ValueError(error)

        try:
            end_date = datetime.strptime(end_date, date_format)
        except ValueError as error:
            raise ValueError(error)

    if start_date >= end_date:
        return None

    urls = list()

    if telescope == 'RTT150':
        url_template = 'http://rtt150meteo.tug.tubitak.gov.tr/ARC-'
    elif telescope == 'T100':
        url_template =\
            'http://t100meteo.tug.tubitak.gov.tr/index.html/Archive/ARC-'
    else:
        url_template =\
            'http://t60meteo.tug.tubitak.gov.tr/index.html/Archive/ARC-'

    d = start_date

    while d < end_date:
        year, month, day = d.year, d.month, d.day
        url = url_template + str(year) + '-' + str(month).zfill(2) +\
            '-' + str(day).zfill(2) + '.txt'

        urls.append(url)
        d = d + timedelta(days=1)

    return urls


def parse_meteo_archive(raw_archive):
    t = pd.read_table(StringIO(raw_archive))

    t.rename(columns={'--Timestamp---': 'Timestamp'}, inplace=True)
    t['Timestamp'] = pd.to_datetime(t['Timestamp'], format='%Y%m%d %H:%M',
                                    errors='coerce')

    t = t.drop(t.index[0])
    t.index = np.arange(0, len(t))

    mask = t['Timestamp'].notna()
    t = t[mask]

    return t


def concat_meteo_archive(tables):
    t = pd.concat(tables)
    t.index = np.arange(0, len(t))

    return t
