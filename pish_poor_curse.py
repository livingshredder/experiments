import argparse
import requests
import hashlib
import time

parser = argparse.ArgumentParser(description='Tests reliability of downloading files from CurseForge API.')
parser.add_argument('-u', '--url', action='store', required=True, help='The URL of the file to download')
parser.add_argument('-m', '--hash', action='store', required=True, help='The hash of the file to download')
parser.add_argument('-t', '--times', action='store', required=False, help='The number of times to download', default=100)

args = parser.parse_args()

times = []
timeouts = 0
mismatches = 0

for i in range(args.times):
    start = time.time()
    print(f'Request {i} of {args.times}')

    r = requests.get(args.url)
    hashstr = hashlib.md5(r.content).hexdigest()
    if hashstr != args.hash:
        print('Hash mismatch!')
        mismatches += 1

    elapsed = time.time() - start
    times.append(elapsed)
