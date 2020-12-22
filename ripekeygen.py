import os

with open('testkey.asc', 'r') as f:
    for line in f.readlines():
        print('certif:	       ' + line, end='')
