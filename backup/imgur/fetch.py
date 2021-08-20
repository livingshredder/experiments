import json
import requests
import mimetypes
from datetime import datetime
from pathlib import Path

API_URL = "https://api.imgur.com/3"
API_TOKEN = ""

headers = {"Authorization": f"Bearer {API_TOKEN}"}

def get_all_images():
    r = requests.get(f"{API_URL}/account/me/images/count", headers=headers)
    r.raise_for_status()

    results = []
    i = 0

    while True:
        r = requests.get(f"{API_URL}/account/me/images/{i}", headers=headers)
        r.raise_for_status()

        images = json.loads(r.content)["data"]
        results.extend(images)
        i = i + 1

        if len(images) == 0:
            break
        print(f"{len(images)} {i}")
    return results

ddir = Path.cwd().joinpath("download")
ddir.mkdir(exist_ok=True)

images = get_all_images()
with ddir.joinpath("metadata.json").open("w") as f:
    f.write(json.dumps(images, indent=4, sort_keys=True))

print(f"downloading {len(images)} images")
for image in images:
    dd = datetime.utcfromtimestamp(image["datetime"])
    ymdir = ddir.joinpath(f"{dd.strftime('%Y-%m')}")
    if not ymdir.exists():
        ymdir.mkdir()
    file_ext = mimetypes.guess_extension(image["type"])
    imgfile = ymdir.joinpath(f"{dd.strftime('%Y-%m-%d_%H-%M-%S')}{file_ext}")
    with requests.get(image["link"], stream=True) as r:
        r.raise_for_status()
        with imgfile.open("wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    print(f"downloaded {image['link']} to {imgfile.name}")
