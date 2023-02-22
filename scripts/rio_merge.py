import rasterio as rio
from rasterio.merge import merge
import argparse
from glob import glob

parser = argparse.ArgumentParser()
parser.add_argument("--output")
parser.add_argument("--inputs", nargs = "+")
args = parser.parse_args()

file_list = args.inputs
output = args.output

##file_list = glob("data/neon/TEAK_2013*.tif")

datasets_to_mosaic = []
for f in file_list:
    src = rio.open(f, "r")
    datasets_to_mosaic.append(src)

mosaic, out_trans = merge(datasets_to_mosaic)

meta = src.meta.copy()
meta.update({
    "height":mosaic.shape[1],
    "width":mosaic.shape[2],
    "transform": out_trans,
    "crs": src.crs
})

with rio.open(output, "w", **meta) as dest:
    dest.write(mosaic)

