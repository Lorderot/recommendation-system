import numpy as np
import pandas as pd
import postgresql
from flask import jsonify
from geopy import distance, Point
from geopy.geocoders import Nominatim
from shapely.geometry import Point as shPoint


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

CHECKINS_BOUND = 20
WORK_AND_STUDY_PCT = 0.3
WORK_OR_STUDY_PCT = 0.4

USE_DB_DRIVER = True


def address_to_coords(address_raw):
    if pd.notnull(address_raw):
        try:
            geolocator = Nominatim()
            location = geolocator.geocode(address_raw)
            return dict(Latitude=location.latitude, Longitude=location.longitude)
        except:
            return {}
    else:
        return {}


def check_validity(polygon_dict, city, coords_list):
    return [
        loc for loc in coords_list if (polygon_dict[city].contains(shPoint(loc['Longitude'], loc['Latitude'])) if
                                       city in polygon_dict.keys() else False)
    ]


def midpoint(POLYGONS_DICT, json_data):
    city = json_data['City']

    valid_checkins = check_validity(POLYGONS_DICT, city, json_data['Coordinates'])
    geo_wk = [v for k, v in json_data.items() if (k in ['Work']) & bool(v)]
    valid_wk = check_validity(POLYGONS_DICT, city, geo_wk)

    geo_st = [v for k, v in json_data.items() if (k in ['Study']) & bool(v)]
    valid_st = check_validity(POLYGONS_DICT, city, geo_st)

    valid_dict = {
        'Work': valid_wk[0] if valid_wk else {},
        'Study': valid_st[0] if valid_wk else {},
        'Check-ins': valid_checkins
    }

    len_checkins = len(valid_checkins)
    if len_checkins >= CHECKINS_BOUND:
        if bool(valid_wk) & bool(valid_st):
            ratio = int(len_checkins * WORK_AND_STUDY_PCT)
            valid_checkins.extend(valid_wk * ratio + valid_st * ratio)
        elif valid_wk:
            ratio = int(len_checkins * WORK_OR_STUDY_PCT)
            valid_checkins.extend(valid_wk * ratio)
        elif valid_st:
            ratio = int(len_checkins * WORK_OR_STUDY_PCT)
            valid_checkins.extend(valid_st * ratio)
        else:
            pass
    else:
        valid_checkins.extend(valid_wk + valid_st)

    if valid_checkins:
        center_dict = {
            'Center_' + ('lat' if k == 'Latitude' else 'long'): np.mean(
                [loc[k] for loc in valid_checkins]) for k in ['Latitude', 'Longitude']
        }
    else:
        center_dict = {
            'Center_' + ('lat' if k == 'Latitude' else 'long'): v for k, v in CITY_CENTERS.get(city, {}).items()
        }
    return center_dict, valid_dict

def center_profits(center_dict, valid_dict, city):
    center_dict['Profits'] = {}
    if valid_dict['Work']:
        center_dict['Profits']['Work_distance'] = distance.distance(
            Point(valid_dict['Work']['Latitude'], valid_dict['Work']['Longitude']),
            Point(center_dict['Center_lat'], center_dict['Center_long'])).km
        center_dict['Profits']['Work_time'] = (center_dict['Profits']['Work_distance'] / CITY_AVG_SPEED.get(
            city, CITY_AVG_SPEED['SAN DIEGO']) * 60.)
    else:
        center_dict['Profits']['Work_distance'] = np.nan
        center_dict['Profits']['Work_time'] = np.nan
    if valid_dict['Study']:
        center_dict['Profits']['Study_distance'] = distance.distance(
            Point(valid_dict['Study']['Latitude'], valid_dict['Study']['Longitude']),
            Point(center_dict['Center_lat'], center_dict['Center_long'])).km
        center_dict['Profits']['Study_time'] = (center_dict['Profits']['Study_distance'] / CITY_AVG_SPEED.get(
            city, CITY_AVG_SPEED['SAN DIEGO']) * 60.)
    else:
        center_dict['Profits']['Study_distance'] = np.nan
        center_dict['Profits']['Study_time'] = np.nan
    return center_dict


def get_real_estate(real_est_df, db_engine, polygons_dict, json_data, use_pandas=False, output_len=500):
    json_data['City'] = json_data['City'].upper()
    json_data['Study'] = address_to_coords(json_data['Study'])
    json_data['Work'] = address_to_coords(json_data['Work'])
    center_dict, valid_dict = midpoint(polygons_dict, json_data)
    if not use_pandas:
        request = (r"SELECT * FROM get_nearest_apartments(" +
                   "{lat}, {long}, '{city_to_search}', {park_count_ge}, {square_feet_ge}, {output_len}, {fake_countryside})")
        request_fmt = request.format(lat=center_dict['Center_lat'],
                                     long=center_dict['Center_long'],
                                     city_to_search=json_data['City'],
                                     park_count_ge=int(json_data['PetsToWalkPresence']),
                                     square_feet_ge=json_data['AmountOfPeopleLiving'] * SQR_METERS_PER_PERSON,
                                     output_len=output_len,
                                     fake_countryside=(not json_data['InCity']))
        try:
            if not USE_DB_DRIVER:
                best_re = pd.read_sql_query(request_fmt, db_engine)
            else:
                db = postgresql.open(db_engine.replace('postgresql', 'pq'))
                get_some = db.query(request_fmt)
                best_re = pd.DataFrame(get_some, columns=get_some[0].column_names)
                db.close()
        except:
            print('DB error. Can not pull N best apartments')
            center_dict = center_profits(center_dict, valid_dict, json_data['City'])
            center_dict['Apartments'] = []
            return jsonify(center_dict)

        if not json_data['InCity']:
            center_dict['Center_lat'], center_dict['Center_long'] = best_re[['latitude', 'longitude']].iloc[0].values
            request_fmt = request.format(lat=center_dict['Center_lat'],
                                         long=center_dict['Center_long'],
                                         city_to_search=json_data['City'],
                                         park_count_ge=int(json_data['PetsToWalkPresence']),
                                         square_feet_ge=json_data['AmountOfPeopleLiving'] * SQR_METERS_PER_PERSON,
                                         output_len=output_len,
                                         fake_countryside=False)
            try:
                if not USE_DB_DRIVER:
                    best_re = pd.read_sql_query(request_fmt, db_engine)
                else:
                    db = postgresql.open(db_engine.replace('postgresql', 'pq'))
                    get_some = db.query(request_fmt)
                    best_re = pd.DataFrame(get_some, columns=get_some[0].column_names)
                    db.close()
            except:
                print('DB error. Can not pull N best apartments')
                center_dict = center_profits(center_dict, valid_dict, json_data['City'])
                center_dict['Apartments'] = []
                return jsonify(center_dict)
    else:
        if not real_est_df.empty:
            sub_df = real_est_df[real_est_df['city'].str.upper() == json_data['City']]
            if not json_data['InCity']:
                temp_df = sub_df[sub_df['is_country_side']]
                temp_df['distance_to_center'] = temp_df[['latitude', 'longitude']].apply(
                    lambda x: distance.distance(Point(x['latitude'], x['longitude']),
                                                Point(center_dict['Center_lat'], center_dict['Center_long'])).km
                    if x.notnull().all() else np.NaN, axis=1)
                center_dict['Center_lat'], center_dict['Center_long'] = (temp_df
                    .sort_values(by=['distance_to_center'], ascending=1)[['latitude', 'longitude']].iloc[0].values)
            else:
                if json_data['PetsToWalkPresence']:
                    sub_df = sub_df[sub_df['num_of_parks'] > 0]
            sub_df = sub_df[sub_df['size_square_feet'] >= json_data['AmountOfPeopleLiving'] * SQR_METERS_PER_PERSON]
            sub_df['distance_to_center'] = sub_df[['latitude', 'longitude']].apply(
                lambda x: distance.distance(Point(x['latitude'], x['longitude']),
                                            Point(center_dict['Center_lat'], center_dict['Center_long'])).km
                if x.notnull().all() else np.NaN, axis=1)
            best_re = sub_df.sort_values(by=['distance_to_center'], ascending=1).iloc[:output_len]
        else:
            center_dict = center_profits(center_dict, valid_dict, json_data['City'])
            center_dict['Apartments'] = []
            return jsonify(center_dict)

    center_dict = center_profits(center_dict, valid_dict, json_data['City'])
    target_to_rename = {
        'latitude': 'Lat',
        'longitude': 'Long',
        'address': 'Address',
        'picture_url': 'Image_url',
        'size_square_feet': 'Area',
        'price': 'Price',
        'leasing_available': 'Leasing_available',
        'distance_to_center': 'Distance_to_center',
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

    best_re['profits'] = best_re[feature_cols].rename(columns=feature_to_rename).apply(
        lambda x: x.astype(bool).to_dict(), axis=1)
    best_re = best_re[target_cols + ['profits']].rename(columns=target_to_rename)
    apartmets_dict = best_re.to_dict(orient='records')
    center_dict['Apartments'] = apartmets_dict
    return jsonify(center_dict)
