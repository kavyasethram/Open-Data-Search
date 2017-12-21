from elasticsearch import Elasticsearch
import json
import certifi

es = Elasticsearch('https://search-opendatasearch-t7hkxgopq34revfqh6bgi5r4kq.us-east-2.es.amazonaws.com',
                    ca_certs=certifi.where())

with open('datasearch.json') as data_file:
    data = json.load(data_file)

count = 0
for d in data:
    count += 1
    try:
        res = es.index(index="datasets", doc_type='dataset', id=count, body=d)
        print(res)
    except:
        continue