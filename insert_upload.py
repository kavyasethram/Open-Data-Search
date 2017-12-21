from elasticsearch import Elasticsearch

es = Elasticsearch()


res = es.search(index="uci_dataset",doc_type='dataset')

print res
