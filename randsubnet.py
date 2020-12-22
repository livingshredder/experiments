import sys
import secrets

prefix = sys.argv[1]
num = int(sys.argv[2])

for i in range(num):
    suffix = secrets.token_hex(2)
    print(prefix + ":" + suffix + "::/64")
