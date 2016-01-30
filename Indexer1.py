import os
import json

from elasticsearch import Elasticsearch


def index(path, titlew, abstractw, authorsw):
    es = Elasticsearch()

    pub_abs_mapping = {
        "pub_abs": {
            "properties": {
                "abstract": {
                    "type": "string",
                    "boost": abstractw
                },
                "authors": {
                    "type": "string",
                    "boost": authorsw
                },
                "citations": {
                    "type": "long"
                },
                "id": {
                    "type": "long"
                },
                "references": {
                    "type": "long"
                },
                "title": {
                    "type": "string",
                    "boost": titlew
                }
            }
        }
    }

    es.indices.create(index="web-search-engine-index-v0.1", body=pub_abs_mapping)

    for file in os.listdir(path):
        json_data = open(path + '\\' + file.title(), encoding="utf-8").read()
        doc = json.loads(json_data)

        es.index(index="web-search-engine-index-v0.1", doc_type="pub_abs", id=int(file.title()), body=doc)

        print('added doc ' + file.title())


path = "C:\\Users\\Mozhdeh\\Documents\\GitHub\\web-search-engine\\json_items_v0.1"
index(path, 1, 1, 1)
