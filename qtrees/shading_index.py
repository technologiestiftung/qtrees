from astral import LocationInfo
from astral.sun import sun
import datetime
import xarray as xr
from pyproj import Proj, transform
import os
import pandas as pd
from qtrees.fisbroker import get_trees
import json

four_selected_dates = {'spring': datetime.date(2022, 3, 21), 'summer': datetime.date(2022, 6, 21),
                       'autumn': datetime.date(2022, 9, 23), 'winter': datetime.date(2022, 12, 21)}
city = LocationInfo(name="Berlin", region="Germany", timezone="Europe/Berlin", latitude=52.5200, longitude=13.4050)
qgis_sun_hours_folder = "data/berlin_sunhours_maps"
data_directory = "data"
trees_file = os.path.join(data_directory, "all_trees_gdf.geojson")
shadow_index_file = 'data/berlin_shadow_index_test.csv'


# calculate theoretical sunhours of the 4 selected days of solstices & equinoxes
def calc_theoretical_daylight(dates, city):
    total_sun_seconds = {}
    for season, date in four_selected_dates.items():
        s = sun(city.observer, date=date, tzinfo=city.timezone)
        for key in ['sunrise', 'sunset']:
            print(f'{key:10s}:', s[key])
        sun_hours = s['sunset'] - s['sunrise']
        print("Daylight hours on the selected day", sun_hours)
        sun_seconds = sun_hours.total_seconds()
        print("Theoretical total seconds of daylight on the selected day", sun_seconds)
        total_sun_seconds[season] = sun_seconds
    print(total_sun_seconds)
    return total_sun_seconds


def calculate_sun_index(seasons_theoretical_daylight, sun_hours_map_directory, tree_json):
    # transform tree coordinates to the crs of sun hours map
    outProj = Proj(init='epsg:25833')
    inProj = Proj(init='epsg:4326')
    actual_sun_hours = {}
    """ goes through the trees & calculates the sun&shadow index per tree for every season 
        based on the ratio of actual sun hours obtained from sun map divided by theoretical daylight
        calculated based on sunrise and sunset hours of the selected representative dates for seasons
    """
    for season, theoretical_daylight in seasons_theoretical_daylight.items():
        seasonal_values = {}
        for filename in os.listdir(sun_hours_map_directory):
            f = os.path.join(sun_hours_map_directory, filename)
            if os.path.isfile(f) and season in filename:
                qgis_sun_hours_map = xr.open_rasterio(f)
                for tree in list(tree_json.items()):
                    baum_id = tree[0]
                    print(baum_id)
                    lat, lon = tree[1]
                    lon, lat = transform(inProj, outProj, lon, lat)
                    tree_marked = qgis_sun_hours_map.sel(x=[lon], y=[lat], method="nearest")
                    tree_actual_sun_hours = float(tree_marked.values)
                    shading_index = tree_actual_sun_hours * 3600 / theoretical_daylight
                    seasonal_values[baum_id] = shading_index
        actual_sun_hours[season] = seasonal_values
        with open('temp_shading.json', 'w') as fp:
            json.dump(actual_sun_hours, fp)
    return actual_sun_hours


def get_sunindex_df(shadow_index_file):
    if not os.path.isfile(shadow_index_file):
        # create json with baumid as key and coordinates as value
        trees_df = get_trees(trees_file)
        simplified_df = trees_df[["baumid", "geometry"]]
        trees_dict = {}
        for baumid, coordinate in simplified_df.itertuples(index=False):
            trees_dict[baumid] = (coordinate.y, coordinate.x)
        seasons_theoretical_daylight = calc_theoretical_daylight(four_selected_dates, city)
        sun_index = calculate_sun_index(seasons_theoretical_daylight, qgis_sun_hours_folder, trees_dict)
        sun_index_df = pd.DataFrame(sun_index)
        shadow_index_df = 1.0 - sun_index_df
        # if file does not exist write header 
        shadow_index_df.to_csv(shadow_index_file)
        return shadow_index_df
    else:
        shadow_index_df = pd.read_csv(shadow_index_file, index_col=0)
        return shadow_index_df

# get_sunindex_df(shadow_index_file)
