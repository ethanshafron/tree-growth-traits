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

bboxes = crowns_wgs.apply(lambda x: x["geometry"].bounds)
ids = crowns_wgs["id"].tolist()

for bbox_of_interest, identity in zip(bboxes, ids):

    time_of_interest = "1984-12-01/2022-12-01"
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )
    #search = catalog.search(
    #    collections=["modis-17A2HGF-061"],
    #    bbox=bbox_of_interest,
    #    datetime=time_of_interest)


    search = catalog.search(
        collections=["landsat-c2-l2"],
        bbox=bbox_of_interest,
        datetime=time_of_interest,
        query={"eo:cloud_cover": {"lt": 10}, "platform": {"in": ["landsat-8", "landsat-9", "landsat-7", "landsat-5"]},},
    )
    site = args.site
    items = search.item_collection()
    print(f"Returned {len(items)} Items")
    data_list = []
    for item in items:
        bands_of_interest = ["red", "green", "blue", "nir08"]
        #data = odc.stac.stac_load(
        #    [item], bands=bands_of_interest, bbox=bbox_of_interest
        #).isel(time=0)
        data = odc.stac.stac_load(
            [item], bands=bands_of_interest, bbox=bbox_of_interest).isel(time=0)

        red = data["red"].astype("float")
        nir = data["nir08"].astype("float")
        blue = data["blue"].astype("float")
        green = data["green"].astype("float")
        #kndvi = np.tanh(((nir-red)/(red+nir))**2)
        
        t = ndvi["time"]
        #gpp = data["Gpp_500m"].astype("float")
        #t = gpp["time"]
        date = t.to_dict()["data"].strftime("%Y-%m-%d").replace("-", "")
        #gpp = gpp.rio.to_crs(epsg = 4326)
        data_frame = pd.DataFrame({"date" : [date],"id":identity, "blue": [blue], "red": [red], "nir08": [nir], "green": [green]})
        data_list.append(data_frame)
out_data = pd.concat(data_list, axis = 0)
out_data.to_csv("landsat_data.csv")













