import json
import requests
import os

input_queries = {}
flare_url = os.getenv('FLARE_URL')
headers = {'content-type': 'application/sq+json'}

with open ("input-queries.json", "r") as rf:
    input_queries = json.load(rf)

for query in input_queries['queries']:
    res = requests.post(flare_url, json=query['sq'], headers=headers)
    query['fhir'] = res.json()

with open ("input-queries-translated.json", "w+") as wf:
    json.dump(input_queries, wf)
