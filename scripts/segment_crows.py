import rasterio as rio
import rasterio.plot
import matplotlib.pyplot as plt
import matplotlib.collections as plt_collection
from skimage import io, segmentation, filters, metrics
import numpy as np
from osgeo import ogr
from osgeo import gdal
import geopandas
from skimage.morphology import erosion
from tqdm import tqdm
from shapely.geometry import shape
from rasterio import features
from multiprocessing import Pool
import itertools
from scipy.stats import mode
import yaml
import argparse
import os


def segment_chm(f, cfg):
    with rio.open(f, "r") as f1:
        grey_image = f1.read(1)
        markers = np.zeros_like(grey_image)
        markers[grey_image < cfg["segmentation"]["marker_min"]] = 1
        markers[grey_image > cfg["segmentation"]["marker_max"]] = 2
        #edge_roberts = filters.roberts(grey_image)
        watershed = segmentation.watershed(grey_image, markers, compactness = cfg["segmentation"]["compactness"])
        if cfg["segmentation"]["local_filter"]:
            filtered = filters.threshold_local(watershed, block_size=cfg["segmentation"]["kernel_size"], method = cfg["segmentation"]["local_filter"])
    
            return filtered, f1.transform
        else:
            return watershed, f1.transform

def get_mask(data):
    mask = data == 2
    return mask.astype(bool)

def get_persistent_site_crowns(site, cfg):
    raster1 = "data/neon" + "/{}_{}{}".format(site, cfg["first_year"], cfg["mosaic_suffix"])
    raster2 = "data/neon" + "/{}_{}{}".format(site, cfg["last_year"], cfg["mosaic_suffix"])
    
    crowns1, crowns_1_transform = segment_chm(raster1, cfg)
    crowns2, crowns_2_transform = segment_chm(raster2, cfg)

    crowns1_mask = get_mask(crowns1)
    crowns2_mask = get_mask(crowns2)

    crowns_1_vecs = []
    for s, value in features.shapes(crowns1.astype("uint8"), mask = crowns1_mask, transform = crowns_1_transform):
        crowns_1_vecs.append(shape(s))

    crowns_2_vecs = []
    for s, value in features.shapes(crowns2.astype("uint8"), mask = crowns2_mask, transform = crowns_2_transform):
        crowns_2_vecs.append(shape(s))

    df1 = geopandas.GeoDataFrame(geometry = crowns_1_vecs)
    df1["area"] = df1.geometry.area

    df2 = geopandas.GeoDataFrame(geometry = crowns_2_vecs)
    df2["area"] = df2.geometry.area
    
    intersection_result = geopandas.overlay(df2, df1, how = "intersection")
    f = rio.open(raster1, "r")
    intersection_result.crs = f.crs
    f.close()
    intersection_result["area"] = intersection_result.geometry.area
    intersection_result = intersection_result.loc[(intersection_result['area'] >= cfg["segmentation"]["min_polygon_size"]) &\
                                                  (intersection_result['area'] <= cfg["segmentation"]["max_polygon_size"])]
    if cfg["sample"]:
        np.random.seed(cfg["seed"])
        intersection_result = intersection_result.sample(cfg["sample"])
    return intersection_result

def run_segmentation_on_all_sites(cfg):
    for site in cfg["sites"]:
        site_crowns = get_persistent_site_crowns(site, cfg)
        site_crowns.to_file("data/crowns/{}_crowns.geojson".format(site))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cfg")
    args = parser.parse_args()
    
    cfg = yaml.safe_load(open("configs/exp_20230222.yaml", "r"))
    
    run_segmentation_on_all_sites(cfg)


if __name__ == "__main__":
    main()







