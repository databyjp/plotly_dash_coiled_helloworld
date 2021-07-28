# ========== (c) JP Hwang 26/7/21  ==========

import pandas as pd
import numpy as np
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
import datashader as ds
import datashader.transfer_functions as tf
from colorcet import fire

# DBC themes: https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

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

# Draw default img
cvs = ds.Canvas(plot_width=800, plot_height=600)
agg = cvs.points(df, agg=ds.mean("trip_distance"), x="pickup_longitude", y="pickup_latitude")
coords_lon, coords_lat = agg.coords['pickup_longitude'].values, agg.coords['pickup_latitude'].values
# Corners of the image, which need to be passed to mapbox
coordinates = [[coords_lon[0], coords_lat[0]],
               [coords_lon[-1], coords_lat[0]],
               [coords_lon[-1], coords_lat[-1]],
               [coords_lon[0], coords_lat[-1]]]

img_out = tf.shade(agg, cmap=fire)[::-1].to_pil()
fig = px.scatter_mapbox(df[:1], lon='pickup_longitude', lat='pickup_latitude', zoom=5)
# Add the datashader image as a mapbox layer image
fig.update_layout(mapbox_style="carto-darkmatter",
                  mapbox_layers=[
                      {
                          "sourcetype": "image",
                          "source": img_out,
                          "coordinates": coordinates
                      }]
                  )

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
                        # dcc.Dropdown(
                        #     id='borough-select',
                        #     options=[{"label": b, "value": b} for b in boroughs],
                        #     multi=True,
                        #     value=list(boroughs)
                        # ),
                        dbc.Label("Show weekday/weekend split"),
                        dcc.Checklist(
                            id='weekday-select',
                            options=[
                                {'label': 'Yes', 'value': 'split'},
                            ],
                            value=['split'],
                        )
                    ])
                ]),
            ], sm=12, md=4),
            dbc.Col([
                dcc.Graph(figure=fig, id="bar-fig-a"),
            ], sm=12, md=8),
        ], className="mt-2"),
        dbc.Row(html.H4("CAB FARE ESTIMATOR".upper()), className="mt-4"),
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

# @app.callback(
#     [Output("bar-fig-a", "figure"),
#      Output("bar-fig-b", "figure")],
#     [Input("hour-slider", "value")],
# )
# def update_bar_fig_a(slider_values):
#
#
#     # bar_fig_a = px.bar(tmp_df, x="day", y="trip_distance", color="dataset", barmode="group",
#     #                    hover_data=["day"], category_orders={'day': day_order}, height=300)
#     # bar_fig_b = px.bar(tmp_df, x="day", y="passenger_count", color="wkend",
#     #                    hover_data=["day"], category_orders={'day': day_order}, height=300)
#     return dash.no_update, dash.no_update


if __name__ == '__main__':
    app.run_server(debug=False)
