# Shell script for launching local Dask scheduler & workers
dask-scheduler &
dask-worker 127.0.0.1:8786 --nprocs 2
python app.py
wait
