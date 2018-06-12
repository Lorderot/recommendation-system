import json
import requests
from time import clock

JSON_TO_SEND = r'input.json'
with open(JSON_TO_SEND) as json_file:
    json_data = json.load(json_file)

request_header = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

st = clock()
resp = requests.post('http://127.0.0.1:3210/api/destination/prod', data=json.dumps(json_data), headers=request_header)
with open('\output.json', 'w') as json_file:
    json.dump(resp.json(), json_file, indent=4)
print(clock() - st, resp.json())
