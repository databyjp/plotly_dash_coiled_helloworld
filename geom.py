# ========== (c) JP Hwang 26/7/21  ==========

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

desired_width = 320
pd.set_option('display.max_columns', 20)
pd.set_option('display.width', desired_width)
import geopandas as gpd

taxi_zones = gpd.read_file('data/taxi_zones/taxi_zones.shp', encoding='utf8')
taxi_zones = taxi_zones.assign(x=taxi_zones["geometry"])

def main():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sh.setFormatter(formatter)
    root_logger.addHandler(sh)


if __name__ == '__main__':
    main()