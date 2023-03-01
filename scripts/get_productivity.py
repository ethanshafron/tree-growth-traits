import pystac_client
import planetary_computer
import odc.stac
import matplotlib.pyplot as plt
import numpy as np
from pystac.extensions.eo import EOExtension as eo
import geopandas as gpd
import rioxarray
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--crowns")
parser.add_argument("--site")
args = parser.parse_args()

f = args.crowns
crowns = gpd.read_file(f)
crowns_wgs = crowns.to_crs(epsg = 4326)
bbox_of_interest = crowns_wgs.total_bounds
time_of_interest = "2012-06-01/2021-06-01"
catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

search = catalog.search(
    collections=["landsat-c2-l2"],
    bbox=bbox_of_interest,
    datetime=time_of_interest,
    query={"eo:cloud_cover": {"lt": 10}, "platform": {"in": ["landsat-8", "landsat-9"]},},
)
site = args.site
items = search.item_collection()
print(f"Returned {len(items)} Items")
for item in items:
    bands_of_interest = ["red", "nir08"]
    data = odc.stac.stac_load(
        [item], bands=bands_of_interest, bbox=bbox_of_interest
    ).isel(time=0)

    red = data["red"].astype("float")
    nir = data["nir08"].astype("float")
    sigma = 0.5
    kndvi = np.tanh(((nir-red)/(red+nir))**2)
    t = kndvi["time"]
    date = t.to_dict()["data"].strftime("%Y-%m-%d").replace("-", "")
    kndvi.rio.to_raster(f"data/productivity/{site}_{date}_kndvi.tif")














