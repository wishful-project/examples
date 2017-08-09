__author__ = "Pierluigi Gallo"
__copyright__ = "Copyright (c) 2017, CNIT"
__version__ = "0.1.0"
__email__ = "pierluigi.gallo@cnit.it"

import networkx as nx
import matplotlib.pyplot as plt


G=nx.DiGraph()
# G.add_node('M', fillcolor='green')
# G.add_edges_from([('B','C'),('C','A'),('A','D'), ('A','E'), ('E','F')]) #define G
# G.add_edge('A','B')
# G['A']['B']['color']='blue'

limits=plt.axis('off')

all_nodes = ['A', 'B', 'C', 'D', 'E', 'F']
G.add_nodes_from(all_nodes)

fixed_positions = {'A': (1800, 2000-2000),
                   'B': (3600, 2000-2000),
                   'C': (5400, 2000-2000),
                   'D': (600, 2000-200),
                   'E': (5990, 2000-200),
                   'F': (4800, 2000-920)}#dict with two of the positions set
fixed_nodes = fixed_positions.keys()
pos = nx.spring_layout(G, pos=fixed_positions, fixed=fixed_nodes)

# transmitting_nodes = ['A', 'E']
tx_nodes_nointerference = ['E']
G.add_nodes_from(tx_nodes_nointerference)
tx_nodes_flowinthemiddle = ['D']
G.add_nodes_from(tx_nodes_flowinthemiddle)
tx_nodes_hiddennodes = ['A']
G.add_nodes_from(tx_nodes_hiddennodes)


carrier_sense_edges = [('D', 'A'), ('A', 'B'), ('B', 'F'), ('B', 'C'), ('F', 'C'), ('F', 'E'), ('E', 'C')]
####### add elements to carrier_sense_edges
# carrier_sense_edges.append(('P', 'q'))
G.add_edges_from(carrier_sense_edges)

transmission_edges = {('A', 'B'): '1Mbps', ('E', 'F'): '2Mbps', ('D', 'A'): '3Mbps'}
##### add elements to transmission_edges
#transmission_edges.update({('P','R'): '344Mpbp'})
G.add_edges_from(transmission_edges.keys())


nx.draw_networkx_nodes(G, pos, all_nodes, arrows=False, node_size=700, node_color='darkgray')
# nx.draw_networkx_nodes(G, pos, transmitting_nodes, arrows=False, node_size=300, node_color='lightgray')

nx.draw_networkx_nodes(G, pos, tx_nodes_nointerference, arrows=False, node_size=300, node_color='green')
nx.draw_networkx_nodes(G, pos, tx_nodes_hiddennodes, arrows=False, node_size=300, node_color='orange')
nx.draw_networkx_nodes(G, pos, tx_nodes_flowinthemiddle, arrows=False, node_size=300, node_color='red')


nx.draw_networkx_edges(G, pos, carrier_sense_edges, edge_color='lightgray',width=2.0,  arrows=False)
nx.draw_networkx_edges(G, pos, transmission_edges, edge_color='black', arrows=True, width=4.0)

nx.draw_networkx_labels(G, pos, labels=None)
nx.draw_networkx_edge_labels(G, pos, edge_labels=transmission_edges)
plt.show()