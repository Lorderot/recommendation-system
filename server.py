from flask import Flask, request, jsonify
import numpy as np


app = Flask(__name__)


def midpoint(json_data):
    geolocations = [v for k, v in json_data['coordinates'].items() if (k in ['work', 'study']) & bool(v)]
    geolocations.extend(json_data['coordinates']['check-ins'])
    if geolocations:
        resp = {
            'latitude': np.mean([float(geoloc['latitude']) for geoloc in geolocations]),
            'longitude': np.mean([float(geoloc['longitude']) for geoloc in geolocations])
        }
    else:
        resp = {}
    return jsonify(resp)


@app.route('/api/destination', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        return midpoint(request.get_json())
    else:
        return 'Geolocations midpoint calculator'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='3210')
