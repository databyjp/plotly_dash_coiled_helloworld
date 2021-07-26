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

day_labels = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}

# DBC themes: https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

day_df = pd.read_csv('data/yellow_tripdata_2019-01_day_grp.csv', index_col=0)
day_df["day"] = day_df["day"].apply(lambda x: day_labels[x])

bar_fig_a = px.bar(day_df, x="day", y="trip_distance", color="wkend",
                   hover_data=["day"], labels=day_labels, height=300)
bar_fig_b = px.bar(day_df, x="day", y="passenger_count", color="wkend",
                   hover_data=["day"], labels=day_labels, height=300)
scatter_fig = px.scatter(day_df, x="tip_per_dist", y="passenger_count", color="wkend", size="count",
                         hover_data=["day"], labels=day_labels, height=300)
scatter_fig.update_layout(margin=dict(l=5, r=5, t=5, b=5))

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
                    dbc.CardHeader(html.H5("This is a test app")),
                    dbc.CardBody('This app shows how Dash apps can be quickly adapted to use Coiled as its back end'),
                ]),
            ], sm=12, md=6),
            dbc.Col([
                dcc.Graph(figure=scatter_fig)
            ], sm=12, md=6),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(figure=bar_fig_a)
            ], sm=12, md=6),
            dbc.Col([
                dcc.Graph(figure=bar_fig_b)
            ], sm=12, md=6),
        ])
    ])
)

app.layout = html.Div([header, body])

if __name__ == '__main__':
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    root_logger.addHandler(sh)

    app.run_server(debug=True)
