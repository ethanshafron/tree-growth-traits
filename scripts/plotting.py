import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

d = gpd.read_file("crowns_intersect_good_filtered.geojson")
t = d.sample(100)
t.to_file("crowns_100.geojson")

df = gpd.read_file("crowns_100_with_data.geojson")
df2 = gpd.read_file("crowns_100_with_13.geojson")
df3 = gpd.read_file("crowns_100_with_18.geojson")
out = df.sjoin(df2, how = "left")
o = out[["geometry", "chm17", "chm13", "Feature_right"]]
o = o.rename(columns = {"Feature_right":"Feature"})

out2 = df3.sjoin(o, how = "left")

gb13  = out2.groupby("Feature_left")["chm13"].mean()
gb18  = out2.groupby("Feature_left")["chm18"].mean()
gb17  = out2.groupby("Feature_left")["chm17"].mean()
plt.clf()
fig, ax = plt.subplots()
ax.scatter(gb13, gb17, c='black')
ax.plot(gb13, gb13, c="red")
#line = mlines.Line2D([0, 1], [0, 1], color='red')
#transform = ax.transAxes
#line.set_transform(transform)
#ax.add_line(line)
plt.xlabel("Mean crown-level height, 2013")
plt.ylabel("Mean crown-level height, 2017")
plt.show()

df2 = df2[df2["chm17"] > 0]
df = df[df["chm13"] > 0]

plt.clf()
plt.hist(df["chm13"], bins = 50)
plt.show()

plt.clf()
plt.hist(df2["chm17"], bins = 50)
plt.show()

gb_m = df2.groupby("Feature")["chm17"].mean()
gb_c = df2.groupby("Feature")["Feature"].count()

plt.clf()
plt.scatter(gb_m, gb_c)
plt.show()

df = df[df["Feature"].isin(df2["Feature"])]
d17 = df2[["Feature", "geometry", "chm17"]]
#d1713 = d17.merge(df[["Feature", "chm13"]], how = "inner", on = "Feature", rsuffix = "13", validate = "one_to_one")
d1713 = pd.merge_ordered(df, d17, right_by = "Feature")
d1713["diff"] = d1713["chm17"] - d1713["chm13"]

d17 = pd.DataFrame(df2[["Feature", "chm17"]])
d13 = pd.DataFrame(df[["Feature", "chm13"]])
dboth = d17.merge(d13, how = "outer", left_on = "Feature", right_on = "Feature")
dboth["diff"] = dboth["chm17"] - dboth["chm13"]

keys = df2[["geometry", "Feature"]]
out = dboth.merge(keys, on = "Feature")
out = gpd.GeoDataFrame(out)
out.crs = df.crs
out.to_file("crowns_201317_diff.geojson")

plt.clf()
plt.hist(out["diff"], bins = 50)
plt.show()

gb_m = out.groupby("Feature_right")["diff"].median()
gb_c = out.groupby("Feature_right")["Feature_right"].count()

plt.clf()
plt.hist(gb_m, bins = 50)
plt.show()

plt.clf()
plt.scatter(out["chm13"], out["chm17"])
plt.show()








