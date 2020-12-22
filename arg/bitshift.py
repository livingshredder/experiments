import os
import sys
from collections import deque

ENCODING = 'ascii'
BYTE_ORDER = 'big'

def decode_str(text):
    byt = []

    octets = int(len(text) / 8)
    for i in range(octets):
        byt.append(int(text[i*8:(i+1)*8], 2).to_bytes(2, byteorder=BYTE_ORDER))

    res = ""
    for b in byt:
        res += b.decode(ENCODING, errors='ignore')
    return res


encoded = sys.argv[1]
if len(encoded) % 8 != 0:
    print('length is not a multiple of 8')
    exit(1)

dmap = dict.fromkeys(range(32))

print('printing all possibilities')
queue = deque(list(encoded))
for i in range(len(encoded)):
    queue.rotate(1)
    result = decode_str(''.join(queue)).translate(dmap)
    
    print(f'{i+1}: {result}')
