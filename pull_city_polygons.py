import pandas as pd
import geopandas as gpd
import osmnx as ox
ox.config(use_cache=True)


USA_CITIES = [
    'SAN DIEGO', 'SAN FRANCISCO'
]


def update_city_polygons(polygons_data_dir):
    polygons_gdf = gpd.GeoDataFrame()
    for city in USA_CITIES:
        city_to_search = '{city}, US'.format(city=city)
        try:
            temp_gdf = ox.gdf_from_place(city_to_search)
            temp_gdf['city'] = city
        except:
            temp_gdf = gpd.GeoDataFrame()
        polygons_gdf = pd.concat([polygons_gdf, temp_gdf])

    polygons_gdf.to_file(polygons_data_dir)
    return polygons_gdf


def convert_gpd_to_dict(polygons_gdf):
    polygons_dict = {}
    for city in USA_CITIES:
        polygons_dict[city] = polygons_gdf.loc[
            polygons_gdf['city'].str.upper() == city, 'geometry'].iloc[0]
    return polygons_dict
