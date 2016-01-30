
from django.shortcuts import render
from elasticsearch import Elasticsearch


def home(request):
	return render(request, "home.html")


def retrieve(request):
	if request.method == 'GET':
		es = Elasticsearch()

		if request.GET['version'] == '0.1':
			res = es.search(index="web-search-engine-index-v0.1", body={"query": {"match": {"_all": request.GET['query']}}}, size=20)
		elif request.GET['version'] == '0.2':
			res = es.search(index="web-search-engine-index-v0.2", body={"query": {"match": {"_all": request.GET['query']}}}, size=20)
		else:
			res = es.search(index="web-search-engine-index-v0.3", body={"query": {"function_score": {
																					"query": {"match": {"_all":  request.GET['query']}},
																					"script_score": {"script": "_score + doc['PageRank'].value"}
																		}}}, size=20)

		# not so neat :D
		clusters = []
		if not request.GET['version'] == '0.1':
			for idx, label in enumerate(clusters_labels):
				dic = {}
				dic['number'] = idx
				dic['title'] = label
				dic['checked'] = True
				clusters.append(dic)

		results = []

		for hit in res['hits']['hits']:
			result = {}

			result['id'] = hit['_id']
			result['score'] = hit['_score']
			result['title'] = hit['_source']['title']
			if hit['_source'].__contains__('cluster'):
				result['cluster'] = clusters[int(hit['_source']['cluster'])]['title']
			else:
				result['cluster'] = 'Not available in this version'
			if hit['_source'].__contains__('PageRank'):
				result['PageRank'] = hit['_source']['PageRank']
			else:
				result['PageRank'] = 'Not available in this version'

			results.append(result)

		return render(request, "search_results.html", {"query": request.GET['query'], "results": results, "clusters": clusters})
	elif request.method == 'POST':
		es = Elasticsearch()

		included_clusters = []

		for cluster_to_be_included in request.POST.getlist('include'):
			included_clusters.append(cluster_to_be_included)

		if request.GET['version'] == '0.2':
			res = es.search(index="web-search-engine-index-v0.2", body={"query": {"filtered": {
																					"query": {"match": {"_all": request.GET['query']}},
																					"filter": {"terms": {"cluster": included_clusters}}
																		}}}, size=20)
		else:
			res = es.search(index="web-search-engine-index-v0.3", body={"query": {"function_score": {
																					"query": {"filtered": {
																								"query": {"match": {"_all": request.GET['query']}},
																								"filter": {"terms": {"cluster": included_clusters}}
																					}},
																					"script_score": {"script": "_score + doc['PageRank'].value"}
																		}}}, size=20)

		clusters = []
		if not request.GET['version'] == '0.1':
			for idx, label in enumerate(clusters_labels):
				dic = {}
				dic['number'] = idx
				dic['title'] = label
				dic['checked'] = included_clusters.__contains__(str(idx))
				clusters.append(dic)

		results = []

		for hit in res['hits']['hits']:
			result = {}

			result['id'] = hit['_id']
			result['score'] = hit['_score']
			result['title'] = hit['_source']['title']
			result['cluster'] = clusters[int(hit['_source']['cluster'])]['title']
			if hit['_source'].__contains__('PageRank'):
				result['PageRank'] = hit['_source']['PageRank']
			else:
				result['PageRank'] = 'Not available in this version'

			results.append(result)

		return render(request, "search_results.html", {"query": request.GET['query'], "results": results, "clusters": clusters})


clusters_labels = []
f = open("C:\\Users\\Mozhdeh\\Documents\\GitHub\\web-based-web-search-engine\\Labels.txt").read().split('\n')
clusters_labels = f[1:]
