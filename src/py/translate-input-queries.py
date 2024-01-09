import json
import requests

if __name__ == "__main__":
    with open('../../config/input-queries.json') as f:
        monitoring_queries = json.load(f)

    flare_url = "http://localhost:8084/query/translate"

    for query in monitoring_queries['queries']:

        header = {
            "Content-Type": "application/sq+json"
        }

        sq = query['sq']
        res = requests.post(flare_url, headers=header, json=sq)
        query["sq-translated"] = res.json()

    with open('../../config/input-queries-translated.json', "w+") as fout:
        json.dump(monitoring_queries, fout)
