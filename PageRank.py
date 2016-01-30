import os
import json
import numpy as np


def save_json_to_file(json_item, filename_convention):
    path = "C:\\Users\\Mozhdeh\\Documents\\GitHub\\web-search-engine\\json_items_v0.3"

    with open(path + '\\' + str(json_item[filename_convention]), 'w', encoding='utf-8') as f:
        json.dump(json_item, f, ensure_ascii=False)


def compute_pagerank(path, threshold, alpha=0.2):
    docs = []
    doc_row_mappings = {}

    print("I'm building the matrix ...")

    for idx, file in enumerate(os.listdir(path)):
        json_data = open(path + '\\' + file.title(), encoding="utf-8").read()
        doc = json.loads(json_data)
        docs.append(doc)
        doc_row_mappings[str(doc['id'])] = idx

    doc_count = len(docs)

    p = np.zeros((doc_count, doc_count), dtype=float)
    t = np.ones((doc_count, doc_count), dtype=float) * 1 / doc_count

    for doc in docs:
        row = doc_row_mappings[str(doc['id'])]
        ref_count = 0
        for ref in doc['references']:
            if doc_row_mappings.__contains__(str(ref)) and doc_row_mappings[str(ref)] != row:
                ref_count += 1

        if ref_count == 0:
            for i in range(0, doc_count):
                p[row, i] = 1 / doc_count
        else:
            for ref in doc['references']:
                if doc_row_mappings.__contains__(str(ref)) and doc_row_mappings[str(ref)] != row:
                    p[row, doc_row_mappings[str(ref)]] = 1 / ref_count

    p = (1 - alpha) * p + alpha * t

    print("I'm now going to compute PageRanks ...")

    x = np.zeros((1, doc_count), dtype=float)
    x[0, 0] = 1

    count = 0
    done = False
    while not done:
        print("Iteration: " + str(count))
        done = True
        xn = x.dot(p)
        for i in range(0, doc_count):
            if abs(xn[0, i] - x[0, i]) > threshold:
                done = False
                break
        x = xn
        count += 1

    for doc in docs:
        doc['PageRank'] = x[0, doc_row_mappings[str(doc['id'])]]
        save_json_to_file(doc, 'id')


path = "C:\\Users\\Mozhdeh\\Documents\\GitHub\\web-search-engine\\json_items_v0.2"
compute_pagerank(path=path, threshold=0.0001)
