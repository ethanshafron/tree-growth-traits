import geopandas as gpd

import numpy as np
from shapely.geometry import Point, Polygon
import pandas as pd

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



f = "data/crowns/first_pass_TEAK_crowns.geojson"
data = polys_to_points(f, 1)








