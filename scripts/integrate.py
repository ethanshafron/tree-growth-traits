import rasterio as rio
import geopandas as gpd
from extract import extract_px_values_to_points
from glob import glob

def integrate_productivity_for_window(files, window_size, df):
    latest_date = files[-1][0]
    earliest_date = latest_date - timedelta(days = 30*window_size)
    this_window_this_year_files = []
    for d, f in files:
        if d <= latest_date and d >= earliest_date:
            this_window_this_year_files.append((d,f))
    this_window_this_year_files = sorted(this_window_this_year_files, key = lambda x:x[0])
    data = [extract_px_values_to_list(f, df) for d, f in this_window_this_year_files]
    timestamps = [toTimestamp(i[0]) for i in this_window_this_year_files]
    integrals = trapezoid(y = np.vstack(data), x=timestamps, axis = 0)
    return integrals

def extract_px_values_to_list(file, data):
    ds = rio.open(file)
    data = data.to_crs(ds.crs)
    xy_pairs = list(zip(data["geometry"].x.tolist(), data["geometry"].y.tolist()))
    samples = [i[0] for i in ds.sample(xy_pairs, 1)]
    ds.close()
    return np.array(samples)

f = "../data/crowns/SJER_TEAK_crowns.geojson"


data = gpd.read_file(f)

frames = [y for x, y in data.groupby('site')]

df = frames[0]
df = df[df["chm_2017"] != -9999]
df = df[df["diff1"] > -5]
chm_col_mask = df.columns.str.startswith("chm")
years = sorted([int(re.findall("[0-9]+", i)[0]) for i in df.columns[chm_col_mask]])
kndvi_files = glob("../data/productivity/SJER_*.tif")
dates = [re.findall("[0-9]+", i)[0] for i in kndvi_files]
date_file_dict = dict(zip(dates, kndvi_files))

files_to_pull_from = {}
for i in range(len(years)):
    files_for_integration = []
    try:
        prior_years = [int(str(i)+"0601") for i in range(years[i], years[i-1]-1, -1)]
        start_date = prior_years[-1]
        end_date = prior_years[0]
        for d in date_file_dict:
            if int(d) >= start_date and int(d) <= end_date:
                files_for_integration.append((d, date_file_dict[d]))
                files_to_pull_from[years[i]] = sorted(files_for_integration, key = lambda x:x[0])
    except IndexError:
        files_to_pull_from[years[i]] = []


import datetime, numpy as np
import calendar
from scipy import stats

def toTimestamp(d):
  return calendar.timegm(d.timetuple())

def get_tree_level_S_and_C(r, window, year1, year2):
    x = r["kndvi_{}_{}".format(window, year)]
    y = r["chm_{}".format(year2)] - r["chm_{}".format(year1)]
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    return slope, r_value**2

SC = df.groupby("id").apply(get_tree_level_S_and_C, window = 12, year1 = 2013, year2 = 2017)
window_size = 10


for year in [2017, 2018, 2019, 2021]:
    files = files_to_pull_from[year]
    files = [(datetime.strptime(i[0], "%Y%m%d"), i[1]) for i in files]
    for window in [2,4,6,8,10,12]:
        df["kndvi_{}_{}".format(window, year)] = integrate_productivity_for_window(files, window, df)



