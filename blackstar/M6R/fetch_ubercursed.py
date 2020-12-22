import uuid
import getch
import argparse
import subprocess
import youtube_dl

def read_cursed(prompt):
    """Replacement for getpass.getpass() which prints asterisks for each character typed"""
    print(prompt, end='', flush=True)
    buf = b''
    while True:
        ch = getch.getch()
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

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--override', action="store_true")
args = parser.parse_args()

if args.override:
    print('DANGER: running in OVERRIDE MODE, output will be shown!!!')

print('ISC armed; BSR Fetch ready for operation')
title = read_cursed('Input BSR title (obfuscated): ')

stdout = subprocess.STDOUT
if args.override:
    stdout = subprocess.DEVNULL

did = uuid.uuid4()

# the phantoms into the darkness
ydl = youtube_dl.YoutubeDL({
    'quiet': True,
    'noplaylist': True,
    'outtmpl': str(did),
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }]
})

result = ydl.download([f'ytsearch:{title}'])
if not result == 0:
    print('youtube-dl seems to have failed?')
    exit(1)

print(f'download success, written to {str(did)}.mp3')
