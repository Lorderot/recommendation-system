from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
from get_real_estate import get_real_estate

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


DATA = (pd.read_sql_query('select * from tb_apartments', os.environ['DEV_DATABASE_URL'])
        .set_index('tb_apartment_id'))


@app.route('/api/destination/prod', methods=['GET', 'POST'])
def prod():
    if request.method == 'POST':
        return get_real_estate(DATA, request.get_json())
    else:
        return 'Real estate filtrator [PROD]'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3210)
    db.init_app(app)
