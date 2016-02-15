#!/usr/bin/env python

import os
import re
from PyPDF2 import PdfFileReader
import datetime
import configparser
import sys
import shutil
from collections import OrderedDict

PATH = os.path.expanduser('~') + '/.config/'
CONFIG = os.path.basename(__file__).split('.py')[0] + '.ini'


def generate_config():
    try:
        os.makedirs(PATH)
    except FileExistsError:
        pass
    config = configparser.ConfigParser(allow_no_value=True)
    config.read_dict(
        OrderedDict((
            ('DEFAULT',
             OrderedDict((
                        ('# Where to scan for the original PDF files.', None),
                        ('path', os.path.join(os.path.expanduser('~'), 'Downloads')),
                        ('\n# The path where to save processed PDF files.', None),
                        ('save_path', os.path.join(os.path.expanduser('~'), 'payments')),
                        ('\n# The template to use when creating the directory in save_path.', None),
                        ('# Valid keywords are provider, year, month and day', None),
                        ('default_tmpl', os.path.join('year', 'provider')),
                     ))
             ),
        ))
    )
    with open(PATH + CONFIG, 'w') as configfile:
        config.write(configfile)


def generate_payment_structure_and_write(
        tmpl, data, path, save_path, pdffile, dt):
    index = 0
    while index < len(tmpl):
        save_path += os.sep + data[tmpl[index]]
        index += 1
    try:
        os.makedirs(save_path)
    except FileExistsError:
        pass
    dst_filename = provider + '.' + dt.strftime('%Y-%m-%d') + '.pdf'
    shutil.copy(
        os.path.join(
            path, pdffile), os.path.join(
            save_path, dst_filename))


def validate_config(config):
    valid_keywords = ['year', 'month', 'day', 'provider']
    default_tmpl = config['DEFAULT']['default_tmpl']
    for i in default_tmpl.strip('/').split('/'):
        if i not in valid_keywords:
            print('ERROR: invalid keyword in default_tmpl. Keyword was: ' + i)
            print('Valid keywords are: ' + ','.join(valid_keywords))
            sys.exit(1)


if __name__ == '__main__':
    # Parse/create config and set minimal values/env for later use
    config = configparser.ConfigParser()
    config.read(os.path.join(PATH, CONFIG))
    try:
        path = config['DEFAULT']['path']
    except KeyError:
        generate_config()
        config.read(os.path.join(PATH, CONFIG))
    validate_config(config)
    path = config['DEFAULT']['path']
    save_path = config['DEFAULT']['save_path']
    default_tmpl = config['DEFAULT']['default_tmpl']
    try:
        os.makedirs(save_path)
    except FileExistsError:
        pass

    # Start crawling directories
    prog = re.compile('[\w ]+_[0-9]{4}.pdf')
    files = [f for f in os.listdir(config['DEFAULT']['path']) if prog.match(f)]
    date_regex = re.compile('.*(\\d{2})[/.-](\\d{2})[/.-](\\d{2}).*')
    time_regex = re.compile('.*(\\d{2})[:.-](\\d{2})[:.-](\\d{2}).*')
    payment_id_regex = re.compile('([0-9]{4})Pago de')
    for pdffile in files:
        pdf1 = PdfFileReader(open(os.path.join(path, pdffile), 'rb'))
        page = pdf1.getPage(0)
        provider = pdffile.split('_')[0]
        text = page.extractText()
        day, month, year = date_regex.match(text).groups()
        hour, minute, second = time_regex.match(text).groups()
        year = '20' + year
        dt = datetime.datetime(
            int(year),
            int(month),
            int(day),
            int(hour),
            int(minute),
            int(second))
        payment_id = payment_id_regex.search(text).groups()[0]
        data = {
            'provider': provider,
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'minute': minute,
            'second': second,
            'payment_id': payment_id,
        }
        generate_payment_structure_and_write(
            default_tmpl.strip('/').split('/'),
            data, path, save_path, pdffile, dt)
