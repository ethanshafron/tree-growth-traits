import requests
import json
import os

SITES = ["SOAP", "SJER", "TEAK"]

PRODUCTS = {"chm": "DP3.30015.001"}

years = [2017, 2018, 2019, 2021]

queries = {}

def wget(url, output):
    r = requests.get(url)
    with open(output, "wb") as f:
        f.write(r.content)



for product in PRODUCTS:
    url = "http://data.neonscience.org/api/v0/products/{}/".format(PRODUCTS[product])
    req = requests.get(url)
    req = json.loads(req.content)
    for i,site in enumerate(req["data"]["siteCodes"]):
        if site["siteCode"] in SITES:
            this_site = site["siteCode"]
            years = [i.split("/")[-1].split("-")[0] for i in site["availableDataUrls"]]
            
            queries[this_site] = dict(zip(years, site["availableDataUrls"]))
url_dict = {}
for site in queries:
    url_dict[site] = {}
    for year in list(queries[site].keys()):
        url_dict[site][year] = {}
        url_dict[site][year]["urls"] = []
        r = requests.get(queries[site][year])
        file_list = json.loads(r.content)["data"]["files"]
        for file in file_list:
            if "CHM" in file["name"]:
                url_dict[site][year]["urls"].append(file["url"])
for site in url_dict:
    for year in url_dict[site]:
        for url in url_dict[site][year]["urls"]:
            maxy = url.split("_")[-2]
            maxx = url.split("_")[-3]
            wget(url, f"data/neon/{site}_{year}_{maxx}_{maxy}_CHM.tif")



