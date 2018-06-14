import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from geopy import distance, Point
from flask import jsonify
from shapely.geometry import Point as shPoint


GOOGLE_MAPS_API_URL = 'http://maps.googleapis.com/maps/api/geocode/json'
CITY_CENTERS = {
    'SAN DIEGO': {
        'Latitude': 32.715736,
        'Longitude': -117.161087,
    },
    'SAN FRANCISCO': {
        'Latitude': 37.773972,
        'Longitude': -122.431297,
    }
}
CITY_AVG_SPEED = {
    'SAN DIEGO': 46.67098,
    'SAN FRANCISCO': 28.96819
}
SQR_METERS_PER_PERSON = 150.


def address_to_coords(address_raw):
    if pd.notnull(address_raw):
        geolocator = Nominatim()
        location = geolocator.geocode(address_raw)
        return dict(Latitude=location.latitude, Longitude=location.longitude) if location else {}
    else:
        return {}


def midpoint(POLYGONS_DICT, json_data):
    city = json_data['City']
    geolocs = [v for k, v in json_data.items() if (k in ['Work', 'Study']) & bool(v)]
    geolocs.extend(json_data['Coordinates'])
    valid_coords = [
        loc for loc in geolocs if (POLYGONS_DICT[city].contains(shPoint(loc['Longitude'], loc['Latitude']))
                                   if city in POLYGONS_DICT.keys() else False)
    ]
    if valid_coords:
        resp = {
            'Center_' + ('lat' if k == 'Latitude' else 'long'): np.mean(
                [loc[k] for loc in valid_coords]) for k in ['Latitude', 'Longitude']
        }
    else:
        resp = {
            'Center_' + ('lat' if k == 'Latitude' else 'long'): v for k, v in CITY_CENTERS.get(city, {}).items()
        }
    resp['Profits'] = {}
    if bool(json_data['Work']) & (json_data['Work'] in valid_coords):
        resp['Profits']['Work_distance'] = distance.distance(
            Point(json_data['Work']['Latitude'], json_data['Work']['Longitude']),
            Point(resp['Center_lat'], resp['Center_long'])).km
        resp['Profits']['Work_time'] = (resp['Profits']['Work_distance'] / CITY_AVG_SPEED.get(
            city, CITY_AVG_SPEED['SAN DIEGO']) * 60.)
    else:
        resp['Profits']['Work_distance'] = np.nan
        resp['Profits']['Work_time'] = np.nan
    if bool(json_data['Study']) & (json_data['Study'] in valid_coords):
        resp['Profits']['Study_distance'] = distance.distance(
            Point(json_data['Study']['Latitude'], json_data['Study']['Longitude']),
            Point(resp['Center_lat'], resp['Center_long'])).km
        resp['Profits']['Study_time'] = (resp['Profits']['Study_distance'] / CITY_AVG_SPEED.get(
            city, CITY_AVG_SPEED['SAN DIEGO']) * 60.)
    else:
        resp['Profits']['Study_distance'] = np.nan
        resp['Profits']['Study_time'] = np.nan
    return resp


def get_real_estate(RE_DF, POLYGONS_DICT, json_data, N_best=500):
    json_data['City'] = json_data['City'].upper()
    json_data['Study'] = address_to_coords(json_data['Study'])
    json_data['Work'] = address_to_coords(json_data['Work'])
    resp_dict = midpoint(POLYGONS_DICT, json_data)
    if not RE_DF.empty:
        sub_df = RE_DF[RE_DF['city'].str.upper() == json_data['City']]
        if json_data['PetsToWalkPresence']:
            sub_df = sub_df[sub_df['num_of_parks'] > 0]

        sub_df = sub_df[sub_df['size_square_feet'] >= json_data['AmountOfPeopleLiving'] * SQR_METERS_PER_PERSON]

        sub_df['dist_to_center'] = sub_df[['latitude', 'longitude']].apply(
            lambda x: distance.distance(Point(x['latitude'], x['longitude']),
                                        Point(resp_dict['Center_lat'], resp_dict['Center_long'])).km
            if x.notnull().all() else np.NaN, axis=1)

        target_to_rename = {
            'latitude': 'Lat',
            'longitude': 'Long',
            'address': 'Address',
            'picture_url': 'Image_url',
            'size_square_feet': 'Area',
            'price': 'Price',
            'leasing_available': 'Leasing_available',
            'dist_to_center': 'Distance_to_center',
            'profits': 'Profits'
        }
        target_cols = [col for col in target_to_rename.keys() if col != 'profits']

        feature_to_rename = {
            'num_of_cafes_rests': 'Cafe_nearby',
            'num_of_cinemas': 'Cinema_nearby',
            'num_of_highways': 'Highway_nearby',
            'num_of_parks': 'Park_nearby'
        }
        feature_cols = list(feature_to_rename.keys())

        best_RE = sub_df[target_cols + feature_cols].sort_values(by=['dist_to_center'], ascending=1).iloc[:N_best]

        best_RE['profits'] = best_RE[feature_cols].rename(columns=feature_to_rename).apply(
            lambda x: x.astype(bool).to_dict(), axis=1)

        best_RE = best_RE[target_cols + ['profits']].rename(columns=target_to_rename)

        apartmets_dict = best_RE.to_dict(orient='records')
    else:
        apartmets_dict = []
    resp_dict['Apartments'] = apartmets_dict
    return jsonify(resp_dict)
