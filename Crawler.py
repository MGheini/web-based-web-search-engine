import json
import time
import requests

from pprint import pprint
from bs4 import BeautifulSoup


def initialize_queue(urls):
    all_doc_ids = []
    initial_json_docs = []

    for url in urls:
        initial_page = requests.get(url)

        soup = BeautifulSoup(initial_page.text, "html.parser")

        data_link = soup.find_all('a', attrs={'class': 'js-publication-title-link js-go-to-publication ga-publication-item'})[:10]
        data_title = soup.find_all('span', attrs={'class': 'publication-title js-publication-title'})[:10]
        data_abstract = soup.find_all('span', attrs={'class': 'full'})[:10]
        data_authors = soup.find_all('div', attrs={'class': 'authors'})[:10]

        for i in range(10):
            doc_id = int(data_link[i].get('href').split('/')[1].split('_')[0])
            if not doc_id in all_doc_ids:
                all_doc_ids.append(doc_id)
                
                json_item = {}

                json_item['id'] = doc_id
                json_item['title'] = data_title[i].text
                json_item['abstract'] = data_abstract[i].text.replace('[Hide abstract] ABSTRACT:', '')

                authors = []
                for a in data_authors[i].find_all('a'):
                    authors.append(a.text)
                authors.append(soup.find('span', attrs={'class': 'fn'}).text)
                json_item['authors'] = authors

                initial_json_docs.append(json_item)

    return initial_json_docs


def extracxt_json_doc(article):
    json_item = {}

    json_item['id'] = article['data']['publicationUid']
    json_item['title'] = article['data']['title']
    json_item['abstract'] = article['data']['abstract']

    authors = []
    for author in article['data']['authors']:
        authors.append(author['fullname'])
    json_item['authors'] = authors

    return json_item


def save_json_to_file(json_item, filename_convention):
    with open(str(json_item[filename_convention]), 'w', encoding='utf-8') as f:
        json.dump(json_item, f, ensure_ascii=False)


def log_frontier_queue(f, incomplete_json_docs):
    f = open('frontier', 'r+')
    f.seek(0)
    # f.write(incomplete_json_docs)

    for item in incomplete_json_docs:
        # f.write("%s\n" % item)
        json.dump(item, f)

    f.truncate()
    f.close()


# TODO: maybe we need to implement this in future
def load_queue_from_log():
    pass


def crawl(urls, max_docs=1000, cite_count=10, ref_count=10):
    all_doc_ids = []

    # create the file for logging the frontier
    log_frontier = open('frontier', 'w')
    log_frontier.close()

    incomplete_json_docs = initialize_queue(urls)
    final_json_docs = []

    for doc in incomplete_json_docs:
        all_doc_ids.append(doc['id'])

    counter = 0
    now = time.time()
    while len(final_json_docs) < max_docs:
        try:
            print('I am working fine ... ' + str(len(final_json_docs)))
            json_doc = incomplete_json_docs.pop(0)
            pUid = json_doc['id']
            cite_referee = 'https://www.researchgate.net/publicliterature.PublicationIncomingCitationsList.html?publicationUid=' + str(
                pUid) + '&usePlainButton=false&showEnrichedPublicationItem=true&useEnrichedContext=true&showAbstract=true&showType=false&showDownloadButton=false&showOpenReviewButton=false&showPublicationPreview=false&swapJournalAndAuthorPositions=true'
            ref_referee = 'https://www.researchgate.net/publicliterature.PublicationCitationsList.html?publicationUid=' + str(
                pUid) + '&usePlainButton=false&showEnrichedPublicationItem=true&showAbstract=true&showType=false&showDownloadButton=false&showOpenReviewButton=false&showPublicationPreview=false&swapJournalAndAuthorPositions=true'
            headers = {'accept': 'application/json', 'x-requested-with': 'XMLHttpRequest'}
            cite_req = requests.get(cite_referee, headers=headers)
            ref_req = requests.get(ref_referee, headers=headers)

            # retrieve references
            references = json.loads(ref_req.text)['result']['data']['citationItems']
            refs = []

            if len(references) > 0 and len(references) < ref_count:
                more_ref_referee = 'https://www.researchgate.net/publicliterature.PublicationCitationsList.html?publicationUid=' + str(
                    pUid) + '&usePlainButton=0&nextDetailPageExperimentViewId=HcydurQm4AtG9oEaYQCyyPcQZp0XsoJgYNk8&swapJournalAndAuthorPositions=1&showAbstract=1&showOpenReviewButton=0&showDownloadButton=0&showType=0&showPublicationPreview=0&showEnrichedPublicationItem=1&dbw=true&publicationUid=' + str(
                    pUid) + '&sort=normal&limit=' + str(ref_count - len(references)) + '&offset=10'
                headers = {'accept': 'application/json', 'x-requested-with': 'XMLHttpRequest'}
                more_ref_req = requests.get(more_ref_referee, headers=headers)

                references.extend(json.loads(more_ref_req.text)['result']['data']['citationItems'])

            for article in references:
                refs.append(article['data']['publicationUid'])

                if not article['data']['publicationUid'] in all_doc_ids:
                    all_doc_ids.append(article['data']['publicationUid'])
                    new_json_doc = extracxt_json_doc(article)
                    incomplete_json_docs.append(new_json_doc)

            # retrieve citations
            citations = json.loads(cite_req.text)['result']['data']['citationItems']
            cites = []

            if len(citations) > 0 and len(citations) < cite_count:
                more_cite_referee = 'https://www.researchgate.net/publicliterature.PublicationIncomingCitationsList.html?publicationUid=' + str(
                    pUid) + '&usePlainButton=0&useEnrichedContext=1&swapJournalAndAuthorPositions=1&showAbstract=1&showOpenReviewButton=0&showDownloadButton=0&showType=0&showPublicationPreview=0&showEnrichedPublicationItem=1&publicationUid=' + str(
                    pUid) + '&limit=' + str(cite_count - len(citations)) + '&offset=3'
                headers = {'accept': 'application/json', 'x-requested-with': 'XMLHttpRequest'}
                more_cite_req = requests.get(more_cite_referee, headers=headers)

                citations.extend(json.loads(more_cite_req.text)['result']['data']['citationItems'])

            for article in citations:
                cites.append(article['data']['publicationUid'])

                if not article['data']['publicationUid'] in all_doc_ids:
                    all_doc_ids.append(article['data']['publicationUid'])
                    new_json_doc = extracxt_json_doc(article)
                    incomplete_json_docs.append(new_json_doc)

            json_doc['references'] = refs
            json_doc['citations'] = cites
            final_json_docs.append(json_doc)

            # save each completed json to a file
            save_json_to_file(json_doc, 'id')

            # save the current frontier for the catastrophic case!
            # every 10 json_item
            if counter % 10 == 0:
                log_frontier_queue(log_frontier, incomplete_json_docs)

            counter += 1
        # if connection was not OK, continue the loop, do not panic!
        except ConnectionError:
            print('I am idle -- waiting for connection ...')
        # if format was json incompatible
        except KeyError:
            print('Skipped an incompatible page ...')
        except requests.exceptions.SSLError:
            print('I am recovering from an SSL error ...')
        except BaseException:
            print('Another exception occured -- but I am still trying ...')

    later = time.time()
    print("All crawling took " + str(int(later-now)) + " onerous seconds.")


crawl(urls=["http://www.researchgate.net/researcher/8159937_Zoubin_Ghahramani",
    "http://www.researchgate.net/researcher/59382974_Jose_Miguel_Hernandez-Lobato"], max_docs=50, cite_count=15, ref_count=15)
