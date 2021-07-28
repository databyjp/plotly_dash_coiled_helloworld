# ========== (c) JP Hwang 26/7/21  ==========

import logging
import pandas as pd
import plotly.express as px
import datashader as ds
import datashader.transfer_functions as tf
from colorcet import fire

logger = logging.getLogger(__name__)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
sh = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
root_logger.addHandler(sh)

desired_width = 320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', desired_width)

df = pd.read_csv("data/yellow_tripdata_2016-01.csv")

# Preprocessing to filter out likely problematic / unrepresentative data
df = df[df["trip_distance"] > 0]
df = df[(df["fare_amount"] > 0) & (df["fare_amount"] < 10000)]
df = df[(df["pickup_longitude"] > -74.15) & (df["pickup_longitude"] < -73.7004) &
      (df["pickup_latitude"] > 40.5774) & (df["pickup_latitude"] < 40.9176)]

# Add new columns
df = df.assign(hour=pd.to_datetime(df["tpep_pickup_datetime"]).dt.hour)
df = df.assign(day=pd.to_datetime(df["tpep_pickup_datetime"]).dt.weekday)
df = df.assign(wkend=df["day"] >= 5)
df = df.assign(triptime=pd.to_datetime(df["tpep_dropoff_datetime"])-pd.to_datetime(df["tpep_pickup_datetime"]))
df = df.assign(avg_spd=df["trip_distance"] / df.triptime.dt.seconds * 3600)

df = df[df["avg_spd"] <= 100]  # NY taxis are fast but not *that* fast

cvs = ds.Canvas(plot_width=800, plot_height=600)
agg = cvs.points(df, agg=ds.mean("trip_distance"), x="pickup_longitude", y="pickup_latitude")

img_out = tf.shade(agg, cmap=fire)[::-1].to_pil()
fig = px.imshow(img_out)
fig.show()


cvs = ds.Canvas(plot_width=800, plot_height=600)
agg = cvs.points(df[(df["hour"] >= 7) & (df["hour"] < 10) & (df["wkend"] == False)], agg=ds.mean("trip_distance"), x="pickup_longitude", y="pickup_latitude")

img_out = tf.shade(agg, cmap=fire)[::-1].to_pil()
fig = px.imshow(img_out)
fig.show()





day_labels = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

df = df[df["trip_distance"] > 0]
df = df[(df["fare_amount"] > 0) & (df["fare_amount"] < 10000)]
ignore_IDs = [264, 265]
df = df[-(df["PULocationID"].isin(ignore_IDs) | df["DOLocationID"].isin(ignore_IDs))]

df = df.assign(hour=pd.to_datetime(df["tpep_pickup_datetime"]).apply(lambda x: x.hour))
df = df.assign(wkend=pd.to_datetime(df["tpep_pickup_datetime"]).apply(lambda x: x.weekday() >= 5))





df = df.assign(hour=pd.to_datetime(df["tpep_pickup_datetime"]).apply(lambda x: x.hour))
df = df.assign(wkend=pd.to_datetime(df["tpep_pickup_datetime"]).apply(lambda x: x.weekday() >= 5))

df = df.assign(day=pd.to_datetime(df["tpep_pickup_datetime"]).apply(lambda x: x.date().weekday()))
df["day"] = df["day"].apply(lambda x: day_labels[x])
df = df.assign(wkend=False)
df.loc[df["day"].isin(['Sat', 'Sun']), "wkend"] = True



# todo - predict fare based on distance, time & wkend
grp_df = df.groupby(["wkend", "hour"]).agg({'tip_amount': 'mean', 'fare_amount': 'mean', 'trip_distance': 'mean', 'passenger_count': 'mean', 'VendorID': 'count'})
grp_df.reset_index(inplace=True)
scatter_fig = px.scatter(grp_df, x="trip_distance", y="fare_amount", size="VendorID", color="hour",
                         color_continuous_scale=px.colors.cyclical.IceFire, facet_col="wkend")
scatter_fig.show()



grp_df = df.groupby(["wkend", "PULocationID"]).agg({'tip_amount': 'median', 'fare_amount': 'median', 'trip_distance': 'median', 'passenger_count': 'mean', 'VendorID': 'count'})

acc_locs = grp_df[(grp_df["VendorID"] > 10000) & (grp_df["VendorID"] > 10000)]

hist_fig = px.histogram(df, x="passenger_count")
hist_fig.show()


df.corr()

day_df = df.groupby("day").agg({'tip_amount': 'mean', 'trip_distance': 'mean', 'passenger_count': 'mean', 'VendorID': 'count'})
day_df = day_df.assign(tip_per_dist=day_df["tip_amount"]/day_df["trip_distance"])
day_df = day_df.rename({'VendorID': 'count'}, axis=1)
day_df.reset_index(inplace=True)
day_df = day_df.assign(wkend=False)
day_df.loc[day_df["day"].isin([5, 6]), "wkend"] = True
day_df = day_df.assign(wkend=False)
day_df.loc[day_df["day"].isin(['Sat', 'Sun']), "wkend"] = True
bar_fig_a = px.bar(day_df, x="day", y="trip_distance", color="wkend",
                         hover_data=["day"])
bar_fig_a.show()
bar_fig_b = px.bar(day_df, x="day", y="passenger_count", color="wkend",
                         hover_data=["day"])
bar_fig_b.show()

scatter_fig = px.scatter(day_df, x="tip_per_dist", y="passenger_count", color="wkend", size="count",
                         hover_data=["day"])
scatter_fig.show()

day_df.to_csv('data/yellow_tripdata_2019-01_day_grp.csv')

pickup_df = df.groupby("PULocationID").agg({'tip_amount': 'mean', 'total_amount': 'mean', 'trip_distance': 'mean', 'passenger_count': 'mean', 'VendorID': 'count'})
pickup_df = pickup_df.assign(tip_per_dist=pickup_df["tip_amount"]/pickup_df["trip_distance"])
pickup_df = pickup_df.assign(tip_per_fare=pickup_df["tip_amount"]/pickup_df["total_amount"])
pickup_df = pickup_df.rename({'VendorID': 'count'}, axis=1)
pickup_df = pickup_df[pickup_df["count"] > 10000]
pickup_df.reset_index(inplace=True)

from sklearn.cluster import AgglomerativeClustering
clusters = AgglomerativeClustering(n_clusters=8).fit(pickup_df[["trip_distance", "tip_per_fare"]])
pickup_df = pickup_df.assign(clust=clusters.labels_)

scatter_fig = px.scatter(pickup_df, x="trip_distance", y="tip_per_fare", size="count", hover_data=["PULocationID"], color="clust")
scatter_fig.show()

hour_df = df.groupby("hour").agg({'tip_amount': 'mean', 'total_amount': 'mean', 'trip_distance': 'mean', 'passenger_count': 'mean', 'VendorID': 'count'})
hour_df = hour_df.assign(tip_per_dist=hour_df["tip_amount"]/hour_df["trip_distance"])
hour_df = hour_df.assign(tip_per_fare=hour_df["tip_amount"]/hour_df["total_amount"])
hour_df = hour_df.rename({'VendorID': 'count'}, axis=1)
hour_df = hour_df[hour_df["count"] > 10000]
hour_df.reset_index(inplace=True)

scatter_fig = px.scatter(hour_df, x="trip_distance", y="tip_per_fare", size="count", color="hour",
                         color_continuous_scale=px.colors.cyclical.IceFire, facet_col="wkend")
scatter_fig.show()

bar_fig = px.bar(hour_df, x="hour", y="trip_distance", color="tip_per_fare",
                 facet_col="wkend", color_continuous_scale=px.colors.sequential.YlOrRd)
bar_fig.show()



hour_df = df.groupby(["wkend", "PULocationID"]).agg({'tip_amount': 'median', 'fare_amount': 'median', 'trip_distance': 'median', 'passenger_count': 'mean', 'VendorID': 'count'})
hour_df.reset_index(inplace=True)
hour_df = hour_df.assign(wkend_hr=hour_df["wkend"].astype(str) + hour_df["PULocationID"].astype(str))
hour_df = hour_df.rename({'VendorID': 'count'}, axis=1)
hour_df = hour_df[hour_df["count"] > 1000]


clusters = AgglomerativeClustering(n_clusters=6).fit(hour_df[["trip_distance", "passenger_count"]])
hour_df = hour_df.assign(clust=clusters.labels_)
scatter_fig = px.scatter(hour_df, x="trip_distance", y="passenger_count", size="count",
                         hover_data=["wkend_hr"], color="wkend", facet_col="clust", facet_col_wrap=2, color_continuous_scale=px.colors.cyclical.IceFire)
scatter_fig.show()




