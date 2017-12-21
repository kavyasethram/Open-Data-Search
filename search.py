from elasticsearch import Elasticsearch

es = Elasticsearch()

query = "cancer"
res = es.search(index="uci_dataset",
                    body={"query":
                                {"multi_match":
                                    {"query": query,
                                     "fields":["Name^2", "Associated_Tasks"]
                                    }
                                }
                        })

print res