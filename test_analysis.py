# ========== (c) JP Hwang 26/7/21  ==========

import logging
import pandas as pd
import plotly.express as px

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

df = pd.read_csv("data/yellow_tripdata_2019-01.csv")
df = df[df["passenger_count"] > 0]

hist_fig = px.histogram(df, x="passenger_count")
hist_fig.show()

df = df.assign(day=pd.to_datetime(df["tpep_pickup_datetime"]).apply(lambda x: x.date().weekday()))

day_df = df.groupby("day").agg({'tip_amount': 'mean', 'trip_distance': 'mean', 'passenger_count': 'mean', 'VendorID': 'count'})
day_df = day_df.assign(tip_per_dist=day_df["tip_amount"]/day_df["trip_distance"])
day_df = day_df.rename({'VendorID': 'count'}, axis=1)
day_df.reset_index(inplace=True)
day_df = day_df.assign(wkend=False)
day_df.loc[day_df["day"].isin([5, 6]), "wkend"] = True

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
