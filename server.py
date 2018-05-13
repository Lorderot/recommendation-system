from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import os

app = Flask(__name__)

# export APP_SETTINGS=config.ProductionConfig
# export APP_SETTINGS=config.DevelopmentConfig
# export APP_SETTINGS=config.TestingConfig
app.config.from_object(os.environ['APP_SETTINGS'])
# suppress warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 10
db = SQLAlchemy(app)
# to help Alembic detect changes in models. Depends on db object
import models


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
    # to get all apartments uncomment the following code
    # db.session.query(models.Apartment).all()
    if request.method == 'POST':
        return midpoint(request.get_json())
    else:
        return 'Geolocations midpoint calculator'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3210)
    db.init_app(app)