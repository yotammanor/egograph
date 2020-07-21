# heavily based on https://gist.github.com/davidADSP/35648e480685c6b57ce1efad50170c26#file-ego_graph-py
from collections import Counter
from csv import DictReader

import matplotlib.pyplot as plt
import networkx as nx

from conf import GRAPH_DB_CSV

ORIGINAL_TERM = 'Amoxicillin'


def main(term=ORIGINAL_TERM):
    edges, nodes = build_formatted_graph_data(term=term)
    print(edges, nodes)
    # BUILD THE INITIAL FULL GRAPH
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    # BUILD THE EGO GRAPH FOR TENSORFLOW
    EG = nx.ego_graph(G, term, distance='distance', radius=15)

    # FIND THE 2-CONNECTED SUBGRAPHS
    subgraphs = nx.algorithms.connectivity.edge_kcomponents.k_edge_subgraphs(EG, k=1)

    # GET THE SUBGRAPH THAT CONTAINS TENSORFLOW
    for s in subgraphs:
        if term in s:
            break
    pruned_EG = EG.subgraph(s)

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


def build_formatted_graph_data(term):
    # SAMPLE DATA FORMAT
    # nodes = [('tensorflow', {'count': 13}),
    # ('pytorch', {'count': 6}),
    # ('keras', {'count': 6}),
    # ('scikit', {'count': 2}),
    # ('opencv', {'count': 5}),
    # ('spark', {'count': 13}), ...]

    # edges = [('pytorch', 'tensorflow', {'weight': 10, 'distance': 1}),
    # ('keras', 'tensorflow', {'weight': 9, 'distance': 2}),
    # ('scikit', 'tensorflow', {'weight': 8, 'distance': 3}),
    # ('opencv', 'tensorflow', {'weight': 7, 'distance': 4}),
    # ('spark', 'tensorflow', {'weight': 1, 'distance': 10}), ...]

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


if __name__ == '__main__':
    main()
