import base64
import argparse
import getpass
import json
import os
import webbrowser
from google import google

idents = []
ident_file = 'iddff.bin'
redact_file = 'redact.json'

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--search', action='store', required=False)
args = parser.parse_args()

with open(redact_file, 'r') as f:
    redact_words = json.load(f)

def read_load():
    # load idents
    if os.path.exists(ident_file):
        with open(ident_file, 'r') as f:
            idents = json.load(f)

    if args.encode is True:
        ident = str(base64.b64encode(bytes(ident, 'utf-8')))
        print(ident)
        if ident not in idents:
            idents.append(ident)
        with open(ident_file, 'w') as f:
            json.dump(idents, f)
        print('saved')
        exit(0)

if args.search is not None:
    idents = []
    while True:
        ident = getpass.getpass(prompt=f'{len(idents)}: ')
        if not ident:
            break
        idents.append(ident)
    print('\n<==========================>')

    query = args.search % tuple(idents)
    results = {}
    for i in google.search(query):
        rtext = f"{i.index}: {i.name} {i.link}"
        for ident in idents:
            rtext = rtext.lower().replace(ident.lower(), ('#'*len(ident)))
        for rword in redact_words:
            rtext = rtext.lower().replace(rword.lower(), ('#'*len(rword)))
        results[i.index] = i.link
        print(rtext)

    print('\n')
    which = input('?: ')
    decision = results[int(which)]
    webbrowser.open(decision)
    exit(0)

print('nothing to do')
exit(1)
