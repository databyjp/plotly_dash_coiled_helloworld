# ========== (c) JP Hwang 26/7/21  ==========

import pandas as pd
import numpy as np
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# DBC themes: https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

df = pd.read_csv("data/yellow_tripdata_2019-01.csv")
taxi_zones = pd.read_csv("data/taxi+_zone_lookup.csv")

# Preprocessing to filter out likely problematic / unrepresentative data
df = df[df["trip_distance"] > 0]
df = df[(df["fare_amount"] > 0) & (df["fare_amount"] < 10000)]
ignore_IDs = [264, 265]  # Unknown locations
df = df[-(df["PULocationID"].isin(ignore_IDs) | df["DOLocationID"].isin(ignore_IDs))]
df = df[df["tpep_pickup_datetime"] < df["tpep_dropoff_datetime"]]

boroughs = np.sort(taxi_zones["Borough"].unique())

# Add new columns
df = df.assign(hour=pd.to_datetime(df["tpep_pickup_datetime"]).dt.hour)
df = df.assign(day=pd.to_datetime(df["tpep_pickup_datetime"]).dt.weekday)
df = df.assign(wkend=df["day"] >= 5)
df = df.assign(triptime=pd.to_datetime(df["tpep_dropoff_datetime"])-pd.to_datetime(df["tpep_pickup_datetime"]))
df = df.assign(avg_spd=df["trip_distance"] / df.triptime.dt.seconds * 3600)

df = df[df["avg_spd"] <= 100]  # NY taxis are fast but not *that* fast

# Group data by desired parameters
avg_fare_per_dist = df["fare_amount"].mean() / df["trip_distance"].mean()
hour_df = df.groupby(["wkend", "hour"]).agg({'tip_amount': 'mean', 'fare_amount': 'mean', 'trip_distance': 'mean', 'passenger_count': 'mean', 'VendorID': 'count', 'avg_spd': 'mean'})
hour_df.reset_index(inplace=True)
hour_df = hour_df.assign(fare_per_dist=hour_df["fare_amount"]/hour_df["trip_distance"]-avg_fare_per_dist)
hour_df = hour_df.assign(tip_per_fare=hour_df["tip_amount"]/hour_df["fare_amount"])
hour_df = hour_df.assign(tip_per_dist=hour_df["tip_amount"]/hour_df["trip_distance"])
hour_df = hour_df.rename({'VendorID': 'count'}, axis=1)

# Build default graphs
bar_fig = px.bar(hour_df, x="hour", y="count", barmode="stack", color="wkend",
                 height=250, title="Pickups by Hour")
bar_fig.update_layout(margin=dict(l=5, r=5, t=30, b=5))

scatter_fig = px.scatter(hour_df, x="trip_distance", y="fare_amount", size="count", color="hour", facet_col="wkend",
                         color_continuous_scale=px.colors.cyclical.IceFire, height=300, title="Yellow Cab Fares vs Distance by Hour")
scatter_fig.update_layout(margin=dict(l=5, r=5, t=50, b=5))

# DASH LAYOUT
header = html.Div(
    dbc.Container([
        html.H3(["Demo Plotly / Coiled App"], className="py-3"),
    ]), className="bg-light"
)

body = html.Div(
    dbc.Container([
        dbc.Row(html.H4("Data overview".upper()), className="mt-4"),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H6("Controls")),
                    dbc.CardBody([
                        dbc.Label("Filter by boroughs"),
                        dcc.Dropdown(
                            id='borough-select',
                            options=[{"label": b, "value": b} for b in boroughs],
                            multi=True,
                            value=list(boroughs)
                        ),
                        dbc.Label("Show weekday/weekend split"),
                        dbc.Checklist(
                            id='weekday-select',
                            options=[{'label': 'Yes', 'value': 'split'}],
                            value=['split'],
                            switch=True,
                        ),
                        dbc.Label("By trip distance"),
                        dcc.RangeSlider(),
                    ])
                ]),
            ], sm=12, md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H6("Select variables")),
                    dbc.CardBody([
                        dcc.Graph(figure=bar_fig, id="bar-fig-a"),
                        dbc.Label("Labels"),
                        dbc.Row([
                            dbc.Col([
                                dcc.Dropdown(
                                    id='var-a',
                                    options=[
                                        {"label": "Fare amount", "value": "fare_amount"},
                                        {"label": "Tip %", "value": "tip_per_fare"},
                                        {"label": "Passengers", "value": "passenger_count"}
                                    ],
                                    value="fare_amount"
                                ),
                            ], className="sm-6"),
                            dbc.Col([
                                dcc.Dropdown(
                                    id='var-b',
                                    options=[
                                        {"label": "Trip distance", "value": "trip_distance"},
                                        {"label": "Average speed", "value": "avg_spd"},
                                    ],
                                    value="trip_distance"
                                ),
                            ], className="sm-6")
                        ])
                    ])
                ]),
                dcc.Graph(figure=scatter_fig, id="bar-fig-b")
            ], sm=12, md=8),
        ], className="mt-2"),
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
    app.run_server(debug=False)
