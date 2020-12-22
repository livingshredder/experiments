import json
import googleapiclient.discovery
from msvcrt import getch

import base64

FILTER_KEYS = [
    'authors',
    'publisher',
    'publishedDate',
    'industryIdentifiers',
    'readingModes',
    'pageCount',
    'printType',
    'categories',
    'averageRating',
    'ratingsCount',
    'maturityRating',
    'language'
]

FILTER_KEYS2 = [
    'country',
    'saleability',
    'isEbook',
    'listPrice',
    'retailPrice',
    'offers'
]

def read_cursed(prompt):
    """Replacement for getpass.getpass() which prints asterisks for each character typed"""
    print(prompt, end='', flush=True)
    buf = b''
    while True:
        ch = getch()
        if ch in {b'\n', b'\r', b'\r\n'}:
            print('')
            break
        elif ch == b'\x08': # Backspace
            buf = buf[:-1]
            print(f'\r{(len(prompt)+len(buf)+1)*" "}\r{prompt}{"*" * len(buf)}', end='', flush=True)
        elif ch == b'\x03': # Ctrl+C
            raise KeyboardInterrupt
        else:
            buf += ch
            print('*', end='', flush=True)
    return buf.decode(encoding='utf-8')

service = googleapiclient.discovery.build('books', 'v1', developerKey='')

print('ISC armed; BSR Books ready for operation')
title = read_cursed('Input BSR title (obfuscated): ')

# execute the request
result = service.volumes().list(q={'isbn': title}).execute()

# find the first match
if not result or not 'items' in result:
    print('request failed or no results found')
    exit(1)

for match in result['items']:
    vol = match['volumeInfo']

    #print(json.dumps(match)) # DO NOT ENABLE

    filtered = { k: vol[k] for k in FILTER_KEYS if k in vol }

    sale = match['saleInfo']
    sale = { k: sale[k] for k in FILTER_KEYS2 if k in sale }
    if 'buyLink' in match['saleInfo']:
        sale['buyLink'] = base64.encodebytes(match['saleInfo']['buyLink'].encode()).decode()

    result = json.dumps({'volumeInfo': filtered, 'saleInfo': sale}, indent=4)

    #if title.lower() in result.lower():
    #    print('Aborting: BSR data in result!!!')
    #    exit(1)
    print(result)
