import json
import requests
import dateutil.parser
from pathlib import Path

API_URL = "https://api.gyazo.com/api"
API_TOKEN = ""

# authenticate
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# warning: there is bullshit with gyazo "videos"
# these must be DELETED otherwise the API will 500
def get_all_images():
    results = []

    i = 1
    per_page = 100
    while True:
        r = requests.get(f"{API_URL}/images", headers=headers, params={"per_page": per_page, "page": i})
        r.raise_for_status()

        images = json.loads(r.content)
        results.extend(images)
        i = i + 1

        if len(images) == 0:
            break
    return results

ddir = Path.cwd().joinpath("download")
ddir.mkdir(exist_ok=True)

images = get_all_images()
with ddir.joinpath("metadata.json").open("w") as f:
    f.write(json.dumps(images, indent=4, sort_keys=True))

print(f"downloading {len(images)} images")
for image in images:
    dd = dateutil.parser.isoparse(image["created_at"])
    ymdir = ddir.joinpath(f"{dd.strftime('%Y-%m')}")
    if not ymdir.exists():
        ymdir.mkdir()
    imgfile = ymdir.joinpath(f"{dd.strftime('%Y-%m-%d_%H-%M-%S')}.{image['type']}")
    with requests.get(image['url'], stream=True) as r:
        r.raise_for_status()
        with imgfile.open("wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    print(f"downloaded {image['url']} to {imgfile.name}")
