
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

		results = []

		for hit in res['hits']['hits']:
			result = {}

			result['id'] = hit['_id']
			result['score'] = hit['_score']
			result['title'] = hit['_source']['title']
			if hit['_source'].__contains__('cluster'):
				result['cluster'] = hit['_source']['cluster']
			else:
				result['cluster'] = 'Not available in this version'
			if hit['_source'].__contains__('PageRank'):
				result['PageRank'] = hit['_source']['PageRank']
			else:
				result['PageRank'] = 'Not available in this version'

			results.append(result)

		return render(request, "search_results.html", {"query": request.GET['query'], "results": results})
