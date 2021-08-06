# Plotly Dash + Coiled / Dask starter demo app

Dask is an open-source Python library for parallel computing and Coiled is a service that allows for the easy provisioning, scaling and management of remote Dask clusters. 
Together, these Plotly partners enable organizations to scale popular data science libraries, including Plotly’s Dash, across parallel computing clusters.

This app is designed to show how quickly an easily a Dash app using Dask on a local cluster can be converted to use a remote cluster with Coiled.

## Important Notes
- The app assumes that the user has a Coiled account, and that **their account credentials have been set up** (e.g. via `coiled login`).
See Coiled's [getting started guide](https://docs.coiled.io/user_guide/getting_started.html) for help.
- Just as a local Python environment is needed with the right packages, a remote environment is required at the Coiled cluster - see the getting started guide, or Coiled's guide on [creating software environments](https://docs.coiled.io/user_guide/software_environment_creation.html).

![Screenshot of Dash+Coiled app](./assets/dash_coiled_screenshot.png?raw=true)

## Additional documentation:
- [Plotly Dash](https://dash.plotly.com/)
- [Coiled - Getting started](https://docs.coiled.io/user_guide/getting_started.html)
- [Dask](https://docs.dask.org/en/latest/)
  
### Dataset
- [NYC Trip record data](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page) 
