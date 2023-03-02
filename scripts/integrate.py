import rasterio as rio
import geopandas as gpd
from extract import extract_px_values_to_points
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import timedelta
import datetime
from dateutil.relativedelta import relativedelta
import re

def integrate_productivity_for_window(files, data):#, window_onset_month, window_length):
    latest_date = files[-1][0]
    #earliest_date = latest_date - timedelta(days = 30*window_size)
    earliest_date = files[0][0]
    ### The last year
    end_year = latest_date.year
    ### The year where we will start our moving window
    start_year = earliest_date.year    
    years_to_compute = list(range(start_year, end_year+1, 1)) 
    year_data = []
    for year in years_to_compute:
        
        #onset = datetime.datetime(year = year, month = window_onset_month, day = 1)
        #start_search = onset + relativedelta(months=-(window_length/2))
        #end_search = onset + relativedelta(months=+(window_length/2))
        this_window_this_year_files = []
        for d, f in files:
            if d <= latest_date and d >= earliest_date:
                this_window_this_year_files.append((d,f))
        #print(year, len(this_window_this_year_files))
        #if len(this_window_this_year_files) > 1:
        this_window_this_year_files = sorted(this_window_this_year_files, key = lambda x:x[0])
        months = [i[0].month for i in this_window_this_year_files]
        all_data = [extract_px_values_to_list(f, data) for dt, f  in this_window_this_year_files]
        every_month_data = pd.DataFrame(np.vstack(all_data))
        every_month_data["month"] = months
        monthly_average_data = every_month_data.groupby("month").mean()
        timestamps = [toTimestamp(i[0]) for i in this_window_this_year_files]
        #print(monthly_average_data)
        year_data.append(np.sum(monthly_average_data, axis = 0))#*(len(timestamps)/window_size)
        #integrals = np.sum(np.vstack(data), axis = 0)/(len(timestamps)/window_size)
        #integrals = np.sum(np.vstack(data), axis = 0)/(30*window_size)
        #integrals = trapezoid(y = np.vstack(data), x=timestamps, axis = 0)
    total_gpp = np.sum(np.vstack(year_data), axis = 0)
    return total_gpp

def extract_px_values_to_list(file, data):
    ds = rio.open(file)
    data = data.to_crs(ds.crs)
    xy_pairs = list(zip(data["geometry"].x.tolist(), data["geometry"].y.tolist()))
    samples = [i[0] for i in ds.sample(xy_pairs, 1)]
    ds.close()
    return np.array(samples)

import datetime, numpy as np
import calendar
from scipy import stats

def toTimestamp(d):
  return calendar.timegm(d.timetuple())

def get_tree_level_S_and_C(r, year1, year2, param):
    x = r["kndvi_{}".format(year2)]
    y = r["chm_{}".format(year2)] - r["chm_{}".format(year1)]
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    if param == "slope":
        return slope
    elif param == "intercept":
        return intercept
    elif param == "r2":
        return r_value**2
    elif param == "p":
        return p_value
    elif param == "r":
        return r_value

f = "../data/crowns/SJER_TEAK_crowns.geojson"

data = gpd.read_file(f)

frames = [y for x, y in data.groupby('site')]

for df in frames:
    site = df["site"].unique()[0]
    print("Working on {}...".format(site))
    try:
        d = gpd.read_file("../data/productivity/{}_crowns_kndvi_extracted.geojson".format(site))
    except:
        #d = df[df["chm_2017"] != -9999]
        #d = d[d["diff1"] > -5]
        #d = d.sample(3000)
        d = df
        chm_col_mask = d.columns.str.startswith("chm")
        years = sorted([int(re.findall("[0-9]+", i)[0]) for i in d.columns[chm_col_mask]])
        kndvi_files = glob("../data/productivity/{}_*.tif".format(site))
        dates = [re.findall("[0-9]+", i)[0] for i in kndvi_files]
        date_file_dict = dict(zip(dates, kndvi_files))
        print(years)
        files_to_pull_from = {}
        for i in range(len(years)):
            files_for_integration = []
            files = [(datetime.datetime.strptime(j, "%Y%m%d"), date_file_dict[j]) for j in date_file_dict.keys()]
            files = sorted(files, key = lambda x:x[0])
            
            latest_date = files[-1][0]
            #earliest_date = latest_date - timedelta(days = 30*window_size)
            earliest_date = files[0][0]
            ### The last year
            end_year = latest_date.year
            ### The year where we will start our moving window
            start_year = earliest_date.year    
            
            prior_years = [datetime.datetime.strptime(str(j)+"0101", "%Y%m%d") for j in range(years[i], years[i-1]-1, -1)]
            try:
                start_date = prior_years[-1]
                end_date = prior_years[0] + relativedelta(months=+5)
                for da, fi in files:
                    if da >= start_date and da <= end_date:
                        files_for_integration.append((da, fi))
                        files_to_pull_from[years[i]] = sorted(files_for_integration, key = lambda x:x[0].timestamp())
            except IndexError:
                files_to_pull_from[years[i]] = []


        onsets = [1, 3, 5, 7, 9, 11]
        wlengths = [6, 12, 18, 24]
        #gpp_arr = np.ones((len(wlengths), len(onsets), d.shape[0]))


        data_dict = {}
        for year in [2017, 2018, 2019, 2021]:
            files = files_to_pull_from[year]
            #files = [(datetime.datetime.strptime(i[0], "%Y%m%d"), i[1]) for i in files]
            d["kndvi_{}".format(year)]  = integrate_productivity_for_window(files, d)#, window_onset_month, window_length)
            #for i, window_onset_month in enumerate(onsets):
            #    print("Working on onset month {}...".format(window_onset_month))
            #    for j, window_length in enumerate(wlengths):
            #        print("Working on window {}...".format(window_length))
            #        d["kndvi_{}_{}_{}".format(window_onset_month, window_length,  year)]  = integrate_productivity_for_window(files, d)#, window_onset_month, window_length)
                    #gpp_arr[j, i, :]  = integrate_productivity_for_window(files, d, window_onset_month, window_length)
                #d["kndvi_{}_{}".format(window, year)] = integrate_productivity_for_window(files, window, d)

        d.to_file("../data/productivity/{}_crowns_kndvi_extracted.geojson".format(site))
        datasets = []
        years = [2013,2017,2018,2019,2021]

        for i in range(1, len(years)):
            sensitivity = d.groupby("id").apply(get_tree_level_S_and_C, year1 = years[i-1], year2 = years[i], param = "slope")
            coupling = d.groupby("id").apply(get_tree_level_S_and_C, year1 = years[i-1], year2 = years[i], param = "r2")
            p_val = d.groupby("id").apply(get_tree_level_S_and_C, year1 = years[i-1], year2 = years[i], param = "p")
            intercept = d.groupby("id").apply(get_tree_level_S_and_C, year1 = years[i-1], year2 = years[i], param = "intercept")
            corr = d.groupby("id").apply(get_tree_level_S_and_C, year1 = years[i-1], year2 = years[i], param = "r")
            datasets.append(pd.DataFrame({"year_SC":np.ones(coupling.shape[0])*years[i], "S": sensitivity, "C": coupling,"p":p_val,"corr": corr,"beta1": intercept, "id": coupling.index}))
        out = pd.concat(datasets, axis = 0)
        out.to_csv("../data/productivity/S_C_values_{}.csv".format(site))

#    onsets = [1, 3, 5, 7, 9, 11]
#    wlengths = [6, 12, 18, 24]

#    datasets = []
#    years = [2013, 2017, 2018, 2019, 2021]
#    d = gpd.read_file("../data/productivity/{}_crowns_kndvi_extracted.geojson".format(site))
#    print([i for i in d.columns])
#        for onset in onsets:
#            for wind in wlengths:
#                print(site, years[i], onset, wind)




