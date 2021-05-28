from argparse import ArgumentParser

from draw_ego_graph import main as draw_ego_graph
from query_google_suggestions import (
    MAX_DB_SIZE,
    NUM_OF_TERMS_IN_ITERATION,
    build_graph_for_term,
)


def main():
    parser = ArgumentParser(description='build "vs" term query graph')
    parser.add_argument('--original-term', action='store', type=str, default="jenkins", required=False)
    parser.add_argument('-n', '--num-terms', action='store', type=int, default=NUM_OF_TERMS_IN_ITERATION,
                        help="for each source term, get top N target terms")
    parser.add_argument('-m', '--max-db-size', action='store', type=int, default=MAX_DB_SIZE,
                        help="stop crawl at this number the latest")
    args = parser.parse_args()
    build_graph_for_term(original_term=args.original_term, max_db_size=args.max_db_size, n_top_terms=args.num_terms)
    draw_ego_graph(term=args.original_term)


if __name__ == '__main__':
    main()
