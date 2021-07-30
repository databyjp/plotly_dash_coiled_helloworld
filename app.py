# ========== (c) JP Hwang 26/7/21  ==========

import pandas as pd
import numpy as np
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

var_x_dict = {"trip_distance": "Trip distance", "avg_spd": "Average speed"}
var_y_dict = {"fare_amount": "Fare amount", "tip_per_fare": "Tip %", "passenger_count": "Passengers"}

# DBC themes: https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/
app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    {
        'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
        'crossorigin': 'anonymous'
    }
])

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

df = df.assign(weekday="Weekday")
df.loc[df["day"] >= 5, "weekday"] = "Weekend"

df = df.assign(triptime=pd.to_datetime(df["tpep_dropoff_datetime"])-pd.to_datetime(df["tpep_pickup_datetime"]))
df = df.assign(avg_spd=df["trip_distance"] / df.triptime.dt.seconds * 3600)

df = df[df["avg_spd"] <= 100]  # NY taxis are fast but not *that* fast

# Group data by desired parameters
avg_fare_per_dist = df["fare_amount"].mean() / df["trip_distance"].mean()


def grp_df(df_in, grpby_vars=["hour"]):
    hour_df = df_in.groupby(grpby_vars).agg({'tip_amount': 'mean', 'fare_amount': 'mean', 'trip_distance': 'mean', 'passenger_count': 'mean', 'VendorID': 'count', 'avg_spd': 'mean'})
    hour_df.reset_index(inplace=True)
    hour_df = hour_df.assign(fare_per_dist=hour_df["fare_amount"]/hour_df["trip_distance"]-avg_fare_per_dist)
    hour_df = hour_df.assign(tip_per_fare=hour_df["tip_amount"]/hour_df["fare_amount"])
    hour_df = hour_df.assign(tip_per_dist=hour_df["tip_amount"]/hour_df["trip_distance"])
    hour_df = hour_df.rename({'VendorID': 'count'}, axis=1)
    return hour_df


# DASH LAYOUT
header = html.Div([
    dbc.Container([
        html.Header(html.H5("Plotly Dash + Coiled | Starter App".upper(), className="fs-4"), className="d-flex flex-wrap justify-content-center my-1 pb-1 border-bottom")
    ]),
    dbc.Container([
        html.H4([html.I(className="fas fa-taxi rounded text-warning py-1 px-1 mr-2"), html.Span(["NYC Taxi".upper()], className="text-warning"), " Data Dashboard".upper()], className="display-5 fw-bold mt-3"),
        html.Div([
            html.P([
                "This dashboard leverages ", html.A("Plotly Dash", href="https://plotly.com/"), " with ", html.A("Coiled.io", href="https://coiled.io/"),
                " to show how quickly and easily powerful, scalable dashboard and analytics apps can be built with these tools.",
            ], className="lead mb-1"),
        ]),
    ])
], className="bg-dark text-light my-0 py-4")

body = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    html.H4("Controls", className="display-5 fw-bold lh-1 mb-3 pb-2 border-bottom"),
                    html.Div([
                        html.H6([html.I(className="fas fa-map-pin rounded text-dark py-1 px-2 mr-2"), "FILTER: By boroughs".upper()]),
                        dcc.Dropdown(
                            id='borough-select',
                            options=[{"label": b, "value": b} for b in boroughs],
                            multi=True,
                            value=list(boroughs)
                        ),
                        html.H6([html.I(className="fas fa-ruler rounded text-dark py-1 px-1 mr-2"), "FILTER: By trip distance".upper()], className="mt-4"),
                        dcc.RangeSlider(
                            id='dist-slider',
                            min=0,
                            max=30,
                            step=1,
                            value=[5, 15],
                            className="mb-0 pb-0",
                        ),
                        html.Div(html.Small(id='dist-slider-legend', className="mt-0 pt-0"), className="mt-0 pt-0"),
                        html.H6([html.I(className="fas fa-calendar-alt rounded text-dark py-1 px-2 mr-2"), "SHOW: Weekday/weekend split".upper()], className="mt-4"),
                        dbc.Checklist(
                            id='wkend-split',
                            options=[{'label': 'Yes', 'value': 'yes'}],
                            value=['yes'],
                            switch=True,
                        ),
                        html.P([
                            dbc.Badge(f"{len(df)}", color="info", id="n-row-selects"), " rows selected from ", dbc.Badge(f"{len(df)}", color="secondary"), " total data rows."
                        ], className="mt-4"),
                    ])
                ], className='bg-light p-3')
            ], sm=12, md=4, className="mr-3"),
            dbc.Col([
                html.H4("Outputs", className="display-5 fw-bold lh-1 mb-3 pb-2 border-bottom"),
                html.H5([html.I(className="fas fa-clock rounded bg-primary text-white py-1 px-1 mr-2"), "Pickups by time of the day".upper()], className="mt-2"),
                dcc.Graph(figure=px.bar(), id="bar-fig"),
                html.H5([html.I(className="fas fa-chart-line rounded bg-primary text-white py-1 px-1 mr-2"), "Explore correlations".upper()], className="mt-3"),
                dbc.Row([
                    dbc.Col([
                        dcc.Dropdown(
                            id='var-x',
                            options=[{"label": v, "value": k} for k, v in var_x_dict.items()],
                            value="trip_distance"
                        ),
                    ], className="sm-6"),
                    dbc.Col([
                        dcc.Dropdown(
                            id='var-y',
                            options=[{"label": v, "value": k} for k, v in var_y_dict.items()],
                            value="fare_amount"
                        ),
                    ], className="sm-6"),
                ]),
                dcc.Graph(figure=px.scatter(), id="scatter-fig")
            ], sm=12, md=7, className="p-3"),
        ], className="g-5 py-5 mt-2"),
        html.Div([
            html.A([html.Img(src="assets/logo-plotly.svg", className="mr-2", height="30px")], href="https://plotly.com/"),
            html.A([html.Img(src="assets/logo-coiled.svg", className="mr-2", height="50px")], href="https://coiled.io/"),
            html.P(html.Small(["Dataset from ", html.A("TLC Trip Record Data", href="https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page"), "."])),
        ]),
    ])
])

app.layout = html.Div([header, body])

@app.callback(
    [Output("bar-fig", "figure"),
     Output("scatter-fig", "figure"),
     Output("dist-slider-legend", "children"),
     Output("n-row-selects", "children")],
    [Input("borough-select", "value"),
     Input("dist-slider", "value"),
     Input("var-x", "value"),
     Input("var-y", "value"),
     Input("wkend-split", "value")],
)
def build_figs(selected_boroughs, dist_range, var_x, var_y, wkend_split):
    if dist_range[1] == 30:
        dist_range = [dist_range[0], df["trip_distance"].max()]
        disp_range = [dist_range[0], "30+"]
    else:
        disp_range = dist_range

    if "yes" in wkend_split:
        split_var = "weekday"
        grpby_vars = ["weekday", "hour"]
    else:
        split_var = None
        grpby_vars = ["hour"]

    # Filter DataFrame from inputs
    filt_locs = taxi_zones[taxi_zones["Borough"].isin(selected_boroughs)]["LocationID"].values
    filt_df = df[(df["PULocationID"].isin(filt_locs)) & (df["trip_distance"] >= dist_range[0]) & (df["trip_distance"] <= dist_range[1])]

    # Build graphs
    hour_df = grp_df(filt_df, grpby_vars)  # Group data by hour
    bar_fig = px.bar(hour_df, x="hour", y="count", barmode="stack", color=split_var,
                     labels={"count": "Pickups", "hour": "Hour", "weekday": "Time of week"},
                     height=250, template="plotly_white")
    bar_fig.update_layout(margin=dict(l=5, r=5, t=10, b=5))

    scatter_fig = px.scatter(hour_df, x=var_x, y=var_y, size="count", color="hour", facet_col=split_var,
                             labels={"weekday": "Time of week", **var_x_dict, **var_y_dict},
                             color_continuous_scale=px.colors.cyclical.IceFire, height=300, template="plotly_white")
    scatter_fig.update_layout(margin=dict(l=5, r=5, t=50, b=5))
    return bar_fig, scatter_fig, f"Showing trips between {disp_range[0]}-{disp_range[1]} miles", str(len(filt_df))


if __name__ == '__main__':
    app.run_server(debug=False)
