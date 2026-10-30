import json, requests
from pathlib import Path

meta = requests.get(
    "https://www.geoboundaries.org/api/current/gbOpen/RWA/ADM1/", timeout=30
).json()
url = meta.get("simplifiedGeometryGeoJSON") or meta["gjDownloadURL"]
print("Downloading:", url)
gj = requests.get(url, timeout=120).json()

out = Path("artifacts/rwanda_provinces.geojson")
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(gj), encoding="utf-8")

print("Saved", out, "with", len(gj["features"]), "features")
for f in gj["features"]:
    print(f["properties"])