import wikipedia
from msvcrt import getch

import re
import json
import base64

# DECODING THESE REDACTIONS IS PROHIBITED
# UNDER INTERNAL SECURITY DESCRIPTOR 0/1.7/6.3/1.0/2
with open("redactions.json", "r") as f:
    BLACKSTAR_REDACTIONS = json.load(f)

def blackstar_clean_text(text: str):
    for i, redaction in enumerate(BLACKSTAR_REDACTIONS):
        decoded = base64.b64decode(redaction).decode('utf-8').strip()
        text = re.sub(re.escape(decoded), f'[BLACKSTAR REDACTED/BSR{i}/TOPSECRET]', text, flags=re.IGNORECASE)
    return text

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

print('ISC armed; BSR Wiki ready for operation')
title = read_cursed('Input BSR title (obfuscated): ')

try:
    summary = wikipedia.page(title, auto_suggest=False)
except:
    print('Wikipedia exception')
    exit(1)

print(blackstar_clean_text(summary.content))
