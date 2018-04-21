from flask import Flask, jsonify, request
import random

app = Flask(__name__)


@app.route('/optimal_region', methods=['POST'])
def find_optimal_region():
    body = request.get_json()
    x1 = float(body['work.x'])
    y1 = float(body['work.y'])
    x2 = float(body['home.x'])
    y2 = float(body['home.y'])
    data = {'region.x': (x1 + x2) / 2.0,
            'region.y': (y1 + y2) / 2.0,
            'region.radius': random.uniform(1.0, 3.0)}
    return jsonify(data)


if __name__ == '__main__':
    app.run()