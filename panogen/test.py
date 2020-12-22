import sys

data = None
with open('data.txt', 'r') as f:
    data = bytearray.fromhex(f.read().rstrip().replace(',', '').replace('0x', ' '))

print(f"{len(data)} bytes.")

with open('data.out', 'wb') as f:
    f.write(data)
