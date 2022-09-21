from argparse import ArgumentParser
from collections import OrderedDict
from csv import DictWriter

import diskcache as dc
import requests

from src.conf import GRAPH_DB_CSV

MAX_DB_SIZE = 100

OUTPUT = 'firefox'  # this is json output, use OUTPUT = 'toolbar' for XML output
LOCALE = "us"
LANG = "en"
BASE_URL = 'http://suggestqueries.google.com/complete/search'

NUM_OF_TERMS_IN_ITERATION = 5
COLUMN_NAMES = ['source', 'target', 'weight', 'id', 'original_term']


def main():
    parser = ArgumentParser(description='build "vs" term query graph')
    parser.add_argument('--original-term', action='store', type=str, default="Amoxicillin", required=False)
    parser.add_argument('-n', '--num-terms', action='store', type=int, default=NUM_OF_TERMS_IN_ITERATION,
                        help="for each source term, get top N target terms")
    parser.add_argument('-m', '--max-db-size', action='store', type=int, default=MAX_DB_SIZE,
                        help="stop crawl at this number the latest")
    args = parser.parse_args()
    build_graph_for_term(term=args.original_term, max_db_size=args.max_db_size, n_top_terms=args.num_terms)


def build_graph_for_term(term, max_db_size=MAX_DB_SIZE, n_top_terms=NUM_OF_TERMS_IN_ITERATION):
    global_term_index = 0
    searched_terms = set()
    terms_to_search = [term]
    with open(GRAPH_DB_CSV.format(original_term=term), 'w', newline='') as f:
        writer = DictWriter(f, fieldnames=COLUMN_NAMES)
        writer.writerow(dict(zip(COLUMN_NAMES, COLUMN_NAMES)))
    while terms_to_search and global_term_index < max_db_size:
        source_term = terms_to_search.pop(0)
        if source_term in searched_terms:
            continue
        else:
            print(f'global_term_index: {global_term_index}')
            searched_terms.add(source_term)
            target_terms = get_target_terms(source_term, n_top_terms=n_top_terms)
            terms_to_search += target_terms
            with open(GRAPH_DB_CSV.format(original_term=term), 'a', newline='') as f:
                writer = DictWriter(f, fieldnames=COLUMN_NAMES)
                for i, target_term in enumerate(target_terms):
                    global_term_index += 1
                    writer.writerow(
                        dict(zip(
                            COLUMN_NAMES,
                            [source_term, target_term, n_top_terms - i, global_term_index, term]
                        )))


def get_target_terms(source_term: str, n_top_terms: int) -> list:
    res = send_request(source_term)
    res_json = res.json()
    target_terms = [suggestion.split(' vs ', 1)[1] for suggestion in res_json[1] if ' vs ' in suggestion]
    filtered_terms = []
    for candidate_target_term in target_terms:
        if (
                (source_term not in candidate_target_term) and
                (' vs ' not in candidate_target_term) and
                (all([filtered_term not in candidate_target_term for filtered_term in filtered_terms]))
        ):
            filtered_terms.append(candidate_target_term)
    final_target_terms = list(OrderedDict(zip(filtered_terms, [None] * len(filtered_terms))).keys())[:n_top_terms]
    print(f'{source_term}-->{final_target_terms}')
    return final_target_terms


def send_request(source_term):
    cache = dc.Cache('google_api_requests')
    request_url = f"{BASE_URL}?&output={OUTPUT}&gl={LOCALE}&hl={LANG}&q={source_term}%20vs%20"
    if request_url not in cache:
        print(f'getting {source_term}.')
        response = requests.get(request_url)
        cache.set(request_url, response)
    else:
        print(f'{source_term} in cache already.')
        response = cache.get(request_url)
    return response


if __name__ == '__main__':
    main()
