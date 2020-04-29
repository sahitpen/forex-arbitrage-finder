import networkx as nx
import matplotlib, matplotlib.pyplot as plot
from PIL import ImageOps, Image

class GraphVisualization:

    def __init__(self):
        matplotlib.use('Agg')

    def draw_graph(self, digraph, output_file, size, edge_weights):
        arrow_size = 0
        node_size = 0
        font_size = 0
        if size == "small":
            node_size = 250
            font_size = 6
            arrow_size = 5
        elif size == "large":
            node_size = 1500
            font_size = 10
            arrow_size = 55

        # set the dimensions of the output plot
        plot.figure(figsize=(20,20))
        plot.box(on=None)
        # draw all parts of the networkx graph
        pos = nx.random_layout(digraph)
        nx.draw_networkx_nodes(digraph, pos, node_size = node_size, node_color='#2c3e50')
        nx.draw_networkx_labels(digraph, pos, font_size=font_size, font_color='w')
        nx.draw_networkx_edges(digraph, pos, edgelist=digraph.edges, edge_color='#3498db',
                               arrows=True, arrowsize=arrow_size)
        # draw edge weights if desired
        if edge_weights:
            edge_labels = nx.get_edge_attributes(digraph,'weight')
            nx.draw_networkx_edge_labels(digraph, pos, edge_labels=edge_labels, label_pos=0.3, font_size=font_size)
        # save the graph as a PNG file
        plot.savefig("static/"+output_file, format="PNG")
        self.crop_graph_image(output_file)

    def create_graph_from_dataframe(self, dataframe):
        digraph = nx.from_pandas_adjacency(dataframe, create_using=nx.DiGraph())
        return digraph

    def crop_graph_image(self, image_file):
        graph_image = Image.open("static/" +image_file)
        graph_image = ImageOps.crop(graph_image, (200,200,150,200))
        graph_image.save("static/" +image_file)
