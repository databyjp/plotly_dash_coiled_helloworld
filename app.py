# ========== (c) JP Hwang 26/7/21  ==========

import logging

# ===== START LOGGER =====
logger = logging.getLogger(__name__)

import pandas as pd
import numpy as np
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

desired_width = 320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', desired_width)

day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
day_labels = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

# DBC themes: https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

# TODO - find out WHEN there is most amount of traffic (and least), and
# TODO - find out WHERE there is most traffic also

df = pd.read_csv("data/yellow_tripdata_2019-01.csv")

# Preprocessing to filter out likely problematic / unrepresentative data
df = df[df["trip_distance"] > 0]
df = df[(df["fare_amount"] > 0) & (df["fare_amount"] < 10000)]
ignore_IDs = [264, 265]  # Unknown locations
df = df[-(df["PULocationID"].isin(ignore_IDs) | df["DOLocationID"].isin(ignore_IDs))]
df = df[df["tpep_pickup_datetime"] < df["tpep_dropoff_datetime"]]

# Add new columns
df = df.assign(hour=pd.to_datetime(df["tpep_pickup_datetime"]).dt.hour)
df = df.assign(day=pd.to_datetime(df["tpep_pickup_datetime"]).dt.weekday)
df = df.assign(wkend=df["day"] >= 5)
df = df.assign(triptime=pd.to_datetime(df["tpep_dropoff_datetime"])-pd.to_datetime(df["tpep_pickup_datetime"]))
df = df.assign(avg_spd=df["trip_distance"] / df.triptime.dt.seconds * 3600)

df = df[df["avg_spd"] <= 50]  # NY taxis are fast but not *that* fast

# Group data by desired parameters
avg_fare_per_dist = df["fare_amount"].mean() / df["trip_distance"].mean()
grp_df = df.groupby(["wkend", "hour"]).agg({'tip_amount': 'mean', 'fare_amount': 'mean', 'trip_distance': 'mean', 'passenger_count': 'mean', 'VendorID': 'count', 'avg_spd': 'mean'})
grp_df.reset_index(inplace=True)
grp_df = grp_df.assign(fare_per_dist=grp_df["fare_amount"]/grp_df["trip_distance"]-avg_fare_per_dist)
grp_df = grp_df.assign(tip_per_fare=grp_df["tip_amount"]/grp_df["fare_amount"])
grp_df = grp_df.assign(tip_per_dist=grp_df["tip_amount"]/grp_df["trip_distance"])
grp_df = grp_df.rename({'VendorID': 'count'}, axis=1)

bar_fig = px.bar(grp_df, x="hour", y="count", barmode="stack", color="wkend", height=200)
bar_fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))

scatter_fig = px.scatter(grp_df, x="trip_distance", y="fare_amount", size="count", color="hour",
                           color_continuous_scale=px.colors.cyclical.IceFire, facet_col="wkend", height=300)
scatter_fig.update_layout(margin=dict(l=5, r=5, t=20, b=5))

# DASH LAYOUT

header = html.Div(
    dbc.Container([
        html.H3(["Demo Plotly / Coiled App"], className="py-3"),
    ]), className="bg-light"
)

body = html.Div(
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H6("This is a test app")),
                    dbc.CardBody('This app shows how Dash apps can be quickly adapted to use Coiled as its back end'),
                ]),
            ], sm=12),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=bar_fig, id="bar-fig-a")
            ], sm=12, md=8),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H6("Volume ")),
                    dbc.CardBody("Although morning traffic ramps up quickly from the lull of 4-5am, the peak number of pick-ups occur at 6-7pm.")
                ]),
            ], sm=12, md=4),
        ], className="mt-2"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H6("How does typical travel distance and cost change across a day?")),
                    dbc.CardBody("The average fare increases almostly linearly with average trip distance, except at certain hours. A closer inspection indicates that the fare is higher during peak hours, indicating that this is caused by traffic and slow travel time.")
                ]),
            ], sm=12, md=4),
            dbc.Col([
                dcc.Graph(figure=scatter_fig, id="bar-fig-b")
            ], sm=12, md=8),
        ], className="mt-2"),
        dbc.Row(html.H3("Find similar neighborhoods - by your own metrics".upper()), className="my-2"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dcc.RangeSlider(
                        id='hour-slider',
                        min=0,
                        max=24,
                        step=1,
                        value=[9, 17]
                    ),
                    dcc.Dropdown(
                        id='prop-select'
                    )
                ]),
            ], sm=12, md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H6("Clustering results")),
                    dbc.CardBody(
                        dcc.Graph(figure=None, id="cluster-output")
                    )
                ])
            ])
        ], className="mt-2")
    ])
)

app.layout = html.Div([header, body])

@app.callback(
    [Output("bar-fig-a", "figure"),
     Output("bar-fig-b", "figure")],
    [Input("hour-slider", "value")],
)
def update_bar_fig_a(slider_values):


    # bar_fig_a = px.bar(tmp_df, x="day", y="trip_distance", color="dataset", barmode="group",
    #                    hover_data=["day"], category_orders={'day': day_order}, height=300)
    # bar_fig_b = px.bar(tmp_df, x="day", y="passenger_count", color="wkend",
    #                    hover_data=["day"], category_orders={'day': day_order}, height=300)
    return dash.no_update, dash.no_update


if __name__ == '__main__':
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    root_logger.addHandler(sh)

    app.run_server(debug=False)
