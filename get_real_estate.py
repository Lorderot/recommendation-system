import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
import overpass
from geopy import distance, Point
from flask import jsonify


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
SQR_METERS_PER_PERSON = 150.


def address_to_coords(address_raw):
    if pd.notnull(address_raw):
        geolocator = Nominatim()
        location = geolocator.geocode(address_raw)
        return dict(Latitude=location.latitude, Longitude=location.longitude) if location else {}
    else:
        return {}


def coords_validation(lat, long, city):
    url = f'node["place"]({lat},{long},{lat + 0.05},{long + 0.05});'
    resp = overpass.API().get(url)
    try:
        detected_city = resp['features'][0]['properties']['gnis:County'].lower()
        if detected_city == city.lower():
            return True
        else:
            return False
    except:
        return False


def midpoint(json_data):
    geolocs = [v for k, v in json_data.items() if (k in ['Work', 'Study']) & bool(v)]
    geolocs.extend(json_data['Coordinates'])
    valid_coords = [loc for loc in geolocs if coords_validation(loc['Latitude'], loc['Longitude'], json_data['City'])]
    if valid_coords:
        resp = {'center_' + k.lower(): np.mean([loc[k] for loc in valid_coords]) for k in ['Latitude', 'Longitude']}
    else:
        resp = {'center_' + k.lower(): v for k, v in CITY_CENTERS.get(json_data['City'].upper(), {}).items()}
    return resp


def get_real_estate(RE_DF, json_data, N_best=500):
    json_data['Study'] = address_to_coords(json_data['Study'])
    json_data['Work'] = address_to_coords(json_data['Work'])
    resp_dict = midpoint(json_data)

    sub_df = RE_DF[RE_DF['city'].str.lower() == json_data['City'].lower()]
    if json_data['PetsToWalkPresence']:
        sub_df = sub_df[sub_df['num_of_parks'] > 0]

    sub_df = sub_df[sub_df['size_square_feet'] >= json_data['AmountOfPeopleLiving'] * SQR_METERS_PER_PERSON]

    sub_df['dist_to_center'] = sub_df[['latitude', 'longitude']].apply(
        lambda x: distance.distance(Point(x['latitude'], x['longitude']),
                                    Point(resp_dict['center_latitude'], resp_dict['center_longitude'])).km
        if x.notnull().all() else np.NaN, axis=1)

    target_cols = [
        'latitude', 'longitude', 'price', 'picture_url', 'size_square_feet', 'dist_to_center',
    ]

    extra_cols = [
        'num_of_cafes', 'num_of_cinemas', 'num_of_highways', 'num_of_parks',
        'num_of_pubs', 'num_of_railway_stations', 'num_of_restaurants'
    ]

    best_RE = sub_df[target_cols + extra_cols].sort_values(by=['dist_to_center'], ascending=1).iloc[:N_best]

    best_RE['profits'] = best_RE[extra_cols].apply(
        lambda x: [col[7:-1].replace('_', ' ').title() for col in extra_cols if x[col] > 0], axis=1)

    best_RE = best_RE[target_cols + ['profits']]

    resp_dict['real_estate'] = best_RE.to_dict(orient='records')
    return jsonify(resp_dict)
