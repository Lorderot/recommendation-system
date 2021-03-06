from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
import geopandas as gpd
from get_real_estate import get_real_estate
import pull_city_polygons as pcpolygon


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


RUN_UNDER_PANDAS = False
DB_ENGINE = os.environ['DEV_DATABASE_URL']
POLYGONS_DATA_DIR = r'polygons\Polygons.shp'


DATA = pd.DataFrame()
if RUN_UNDER_PANDAS:
    try:
        DATA = (pd.read_sql_query('SELECT * FROM tb_apartments', DB_ENGINE).set_index('tb_apartment_id'))
    except:
        pass


try:
    POLYGONS_DATA = gpd.read_file(POLYGONS_DATA_DIR)
except:
    POLYGONS_DATA = pcpolygon.update_city_polygons(POLYGONS_DATA_DIR)
POLYGONS_DICT = pcpolygon.convert_gpd_to_dict(POLYGONS_DATA)


@app.route('/api/destination/prod', methods=['GET', 'POST'])
def prod():
    if request.method == 'POST':
        return get_real_estate(DATA, DB_ENGINE, POLYGONS_DICT, request.get_json(), use_pandas=RUN_UNDER_PANDAS)
    else:
        return 'Real estate filtrator [PROD]'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
    db.init_app(app)
