
from django.shortcuts import render
from elasticsearch import Elasticsearch

def home(request):
	return render(request, "home.html")

def retrieve(request):
	es = Elasticsearch()

	if request.GET['version'] == '0.1':
		res = es.search(index="web-search-engine-index", body={"query": {"match": {"_all" : request.GET['query']}}})

	results = []

	for hit in res['hits']['hits']:
		result = {}

		result['id'] = hit['_id']
		result['score'] = hit['_score']
		result['title'] = hit['_source']['title']

		results.append(result)

	return render(request, "search_results.html", {"query": request.GET['query'], "results": results})
