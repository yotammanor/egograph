# heavily based on https://gist.github.com/davidADSP/35648e480685c6b57ce1efad50170c26#file-ego_graph-py
from collections import Counter
from csv import DictReader

import matplotlib.pyplot as plt
import networkx as nx

from src.conf import GRAPH_DB_CSV

K_EDGE_SUBGRAPHS = 2
GRAPH_RADIUS = 30


def main(term: str, k_edge_subgraphs: int = K_EDGE_SUBGRAPHS, graph_radius: int = GRAPH_RADIUS) -> None:
    edges, nodes = build_formatted_graph_data(term=term)
    print(f'{edges=}')
    print(f'{nodes=}')
    G = _build_graph_object(edges, nodes)

    pruned_EG = _prune_graph(G, term, graph_radius=graph_radius, k_edge_subgraphs=k_edge_subgraphs)

    _draw_graph(pruned_EG, term)


def build_formatted_graph_data(term):
    print('loading and formatting graph data')
    with open(GRAPH_DB_CSV.format(original_term=term), 'r') as f:
        reader = DictReader(f)
        rows = [row for row in reader]
    nodes_counter = Counter(row['source'] for row in rows) + Counter(row['target'] for row in rows)
    nodes = [(node, {'count': count}) for node, count in nodes_counter.items()]
    edges_dict = dict()
    for row in rows:
        if (row['source'], row['target']) in edges_dict or (row['target'], row['source']) in edges_dict:
            edges_dict[(row['target'], row['source'])][2]['weight'] += int(row['weight'])
            edges_dict[(row['target'], row['source'])][2]['distance'] -= int(row['weight'])
        else:
            edges_dict[(row['source'], row['target'])] = (
                (row['source'], row['target'], {'weight': int(row['weight']), 'distance': 11 - int(row['weight'])}))
    edges = list(edges_dict.values())
    return edges, nodes


def _build_graph_object(edges, nodes) -> nx.Graph:
    print('building graph object')
    # BUILD THE INITIAL FULL GRAPH
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G


def _prune_graph(G, term, graph_radius, k_edge_subgraphs):
    print('pruning graph')
    # BUILD THE EGO GRAPH FOR 'TERM'
    EG = nx.ego_graph(G, term, distance='distance', radius=graph_radius)
    # FIND THE K-CONNECTED SUBGRAPHS
    subgraphs = nx.algorithms.connectivity.edge_kcomponents.k_edge_subgraphs(EG, k=k_edge_subgraphs)
    # GET THE SUBGRAPH THAT CONTAINS 'TERM'
    for s in subgraphs:
        if term in s:
            break
    pruned_EG = EG.subgraph(s)
    return pruned_EG


def _draw_graph(pruned_EG, term):
    print('drawing graph')
    pos = nx.spring_layout(pruned_EG)
    label_pos = {k: (v[0], v[1] - 0.04) for k, v in pos.items()}
    nx.draw_networkx_nodes(pruned_EG, pos, node_color='b', node_size=100)
    for edge in pruned_EG.edges:
        nx.draw_networkx_edges(pruned_EG, pos, edgelist=[edge], width=pruned_EG.get_edge_data(*edge)['weight'],
                               alpha=0.3)
    # Draw ego as large and red
    nx.draw_networkx_nodes(pruned_EG, pos, nodelist=[term], node_size=600, node_color='r')
    nx.draw_networkx_labels(pruned_EG, label_pos, font_size=10)
    plt.show()


if __name__ == '__main__':
    term = input('term: ')
    main(term=term)
