import geopandas as gpd
import matplotlib.pyplot as plt
import rasterio as rio
import numpy as np
from shapely.geometry import Point, Polygon
import pandas as pd
import yaml
from glob import glob
import re
def create_points_in_polygon(polygon, spacing):
    # Get the bounds of the polygon
    minx, miny, maxx, maxy = polygon.bounds    
    # ---- Initialize spacing and point counter
    # Start while loop to find the better spacing according to tolérance increment
    # --- Generate grid point coordinates
    x = np.arange(np.floor(minx), int(np.ceil(maxx)), spacing)
    y = np.arange(np.floor(miny), int(np.ceil(maxy)), spacing)
    xx, yy = np.meshgrid(x,y)
    # ----
    pts = [Point(X-(spacing/2),Y-(spacing/2)) for X,Y in zip(xx.ravel(),yy.ravel())]
    # ---- Keep only points in polygons
    points = [pt for pt in pts if pt.within(polygon)]
    # ---- Verify number of point generated
    point_counter = len(points)
    # ---- Return
    return points

def polys_to_points(f, spacing):
    df = gpd.read_file(f)
    points = []
    polys = list(df["geometry"])
    for index, polygon in enumerate(polys):
        point_data = create_points_in_polygon(polygon, spacing)
        n_points = len(point_data)
        points.append(pd.DataFrame.from_dict({"id": np.ones((n_points,), np.int16)*index , "geometry": pd.Series(point_data)}, orient = "columns"))

    pdf = pd.concat(points)

    df = df.drop(columns = "geometry").reset_index()

    out = pdf.merge(df, how = "left", left_on = "id", right_on = "index")
    out = gpd.GeoDataFrame(out)
    out.crs = df.crs
    out = out.drop(columns = "index")
    return out
def make_plots(data, site):    
    data["diff1"] = data["chm_2017"] - data["chm_2013"]
    data = data[(data != -9999).all(1)]
    gb1 = data.groupby("id")["chm_2013"].mean()
    gb2 = data.groupby("id")["chm_2017"].mean()
    gb3 = data.groupby("id")["chm_2018"].mean()
    gb4 = data.groupby("id")["chm_2019"].mean()
    gb5 = data.groupby("id")["chm_2021"].mean()
    
    plt.clf()
    fig, ax = plt.subplots()
    ax.scatter(gb1, gb2, c='black')
    ax.plot(gb1, gb1, c="red")
    plt.xlabel("Mean crown-level height, 2013")
    plt.ylabel("Mean crown-level height, 2017")
    plt.savefig("Desktop/thesis/figures/{}_height_diff_2013_2017.png".format(site), dpi = 400)
    plt.clf()
    fig, ax = plt.subplots()
    ax.scatter(gb2, gb3, c='black')
    ax.plot(gb2, gb2, c="red")
    plt.xlabel("Mean crown-level height, 2017")
    plt.ylabel("Mean crown-level height, 2018")
    plt.savefig("Desktop/thesis/figures/{}_height_diff_2017_2018.png".format(site), dpi = 400)
    plt.clf()
    fig, ax = plt.subplots()
    ax.scatter(gb3, gb4, c='black')
    ax.plot(gb3, gb3, c="red")
    plt.xlabel("Mean crown-level height, 2018")
    plt.ylabel("Mean crown-level height, 2019")
    plt.savefig("Desktop/thesis/figures/{}_height_diff_2018_2019.png".format(site), dpi = 400)
    plt.clf()
    fig, ax = plt.subplots()
    ax.scatter(gb4, gb5, c='black')
    ax.plot(gb4, gb4, c="red")
    plt.xlabel("Mean crown-level height, 2019")
    plt.ylabel("Mean crown-level height, 2021")
    plt.savefig("Desktop/thesis/figures/{}_height_diff_2019_2021.png".format(site), dpi = 400)
    plt.clf()
    fig, ax = plt.subplots()
    ax.scatter(gb1, gb5, c='black')
    ax.plot(gb1, gb1, c="red")
    plt.xlabel("Mean crown-level height, 2013")
    plt.ylabel("Mean crown-level height, 2021")
    plt.savefig("Desktop/thesis/figures/{}_height_diff_2013_2021.png".format(site), dpi = 400)

cfg = yaml.safe_load(open("Desktop/thesis/configs/exp_20230222.yaml", "r"))

for site in cfg["sites"]:
    files = [i for i in glob("Desktop/thesis/data/neon/{}*{}".format(site, cfg["mosaic_suffix"])) if any(xs in i for xs in cfg["sites"])]
    fields = [cfg["chm_fields"].format(year = re.findall( "_([^_]+)_", i)[0]) for i in files]
    f = f"~/Desktop/thesis/data/crowns/first_pass_{site}_crowns.geojson"
    data = polys_to_points(f, 1)
    for file, field in zip(files, fields):
        xy_pairs = list(zip(data["geometry"].x.tolist(), data["geometry"].y.tolist()))
        ds = rio.open(file)
        samples = [i[0] for i in ds.sample(xy_pairs, 1)]
        data[field] = samples
        ds.close()

    
    make_plots(data, site)









