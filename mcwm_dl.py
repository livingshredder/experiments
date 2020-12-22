import requests
import urllib
import re

prefix = urllib.parse.quote('http://minecraftworldshare.com/mapdownload.aspx?mapid=')

print('requesting all URLs')
response = requests.get(f'http://web.archive.org/cdx/search/cdx?url={prefix}&matchType=prefix&output=json')
results = response.json()

# filter by octet-stream
candidates = []
urls = []
for result in results:
    result = {
        'urlkey': result[0],
        'timestamp': result[1],
        'original': result[2],
        'mimetype': result[3],
        'statuscode': result[4],
        'digest': result[5],
        'length': result[6]
    }

    # ensure status dcode 200 and octet
    if result['statuscode'] != '200':
        continue
    if result['mimetype'] != 'application/octet-stream':
        continue
    if result['urlkey'] in urls:
        continue

    candidates.append(result)
    urls.append(result['urlkey'])

print(candidates)
print(len(candidates))

print(f'downloading {len(candidates)} maps')

for result in candidates:
    timestamp = result['timestamp']
    url = urllib.parse.quote(result['original'])
    print(f'downloading {url}')

    r = requests.get(f'http://web.archive.org/web/{timestamp}/{url}')
    d = r.headers['content-disposition']
    fname = re.findall("filename=(.+)", d)[0]
    with open(f'maps/{fname}', 'wb') as f:
        f.write(r.content)
