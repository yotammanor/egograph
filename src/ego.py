from argparse import ArgumentParser

from src.draw_ego_graph import (
    GRAPH_RADIUS,
    K_EDGE_SUBGRAPHS,
    main as draw_ego_graph,
)
from src.query_google_suggestions import (
    MAX_DB_SIZE,
    NUM_OF_TERMS_IN_ITERATION,
    build_graph_for_term,
)


def main():
    parser = ArgumentParser(description='build "vs" term query graph')
    parser.add_argument('term', action='store', type=str)
    parser.add_argument('-n', '--num-terms', action='store', type=int, default=NUM_OF_TERMS_IN_ITERATION,
                        help="for each source term, get top N target terms")
    parser.add_argument('-m', '--max-db-size', action='store', type=int, default=MAX_DB_SIZE,
                        help="stop crawl at this number the latest")
    parser.add_argument('--graph-radius', action='store', type=int, default=GRAPH_RADIUS,
                        help="max radius of pruned graph")
    parser.add_argument('--k-edge-subgraphs', action='store', type=int, default=K_EDGE_SUBGRAPHS,
                        help="connectedness to original term")

    args = parser.parse_args()
    build_graph_for_term(term=args.term, max_db_size=args.max_db_size, n_top_terms=args.num_terms)
    draw_ego_graph(term=args.term, k_edge_subgraphs=args.k_edge_subgraphs, graph_radius=args.graph_radius)


if __name__ == '__main__':
    main()
