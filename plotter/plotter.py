from pymongo import MongoClient
from graph import Graph
import plotly.graph_objects as go
import plotly.io as pio
import igraph as ig


class Plotter:
    """
    Plotter fetches all documents from the sods collection, organizes the
    data in a custom graph and creates the graph needed to display the data.

    attr:
        - db (mongo database): Pointer to an opened mongodb database.
        - raw_graph (Graph): Processed data retrieved from db.
    """

    def __init__(self, mongo_uri, max_tags):
        self.db = self.mongo_setup(mongo_uri)
        self.raw_graph = self.process_data(max_tags)

    def process_data(self, max_tags):
        """
        Create an instance of a custom graph and pre process
        all data available in the mongodb collection.

        params:
            - max_tags (int): only the top max_tags will be kept to display.

        returns:
            - Graph: an organized structure of how the data
                should be displayed.
        """

        raw_graph = Graph()
        for doc in self.db.stackoverflowdataset.find():
            raw_graph.add_document(doc)

        return self.trim_raw_graph(raw_graph, max_tags)

    def trim_raw_graph(self, graph, max_tags):
        """
        Sort and only keep top most used tags. Remove remaining nodes and edges.

        params:
            - graph (Graph): the organized data loaded from the database.
            - max_tags (int): number of nodes that will be displayed.

        returns:
            - trimmed graph with only max_tags of nodes.
        """

        graph.nodes = {
            k: v
            for k, v in sorted(
                graph.nodes.items(), key=lambda node: node[1].weight, reverse=True
            )[:max_tags]
        }

        for n1, n2 in list(graph.edges.keys()):
            if n1 not in graph.nodes or n2 not in graph.nodes:
                del graph.edges[(n1, n2)]

        return graph

    def mongo_setup(self, mongo_uri):
        """
        Connect to the mongo instance and return the database.

        params:
            - mongo_uri (str): class is instantiated with string.

        returns:
            - pointer to mongo database
        """

        client = MongoClient(mongo_uri)
        return client["stackoverflowdataset"]

    def create_graph(self):
        """
        Since igraph stores the graph structure in indexed c-style arrays,
        all attributes and labels need to be organized similarly.
        These data is organized, loaded in Scatter3d class from plotly,
        and the resulting graph is saved in a "plot.html" file which gets
        automatically opened in the browser if available.
        """

        N = len(self.raw_graph.nodes)

        # load all min and max ranges to scale node sizes
        max_we, min_we = self.minmax_weights()
        max_vo, min_vo = self.minmax_votes()
        max_vi, max_an, min_an = self.max_views_answers()

        # igraph stores nodes and edges as C-style arrays indexed by int.
        # labels and attributes correspond to the ordered indeces.
        nodes, edges, nodes_labels, edges_labels = self.c_style_arrays()

        # generate sizes and colors of nodes in indexed arrays.
        sizes, colors = self.attr(
            nodes, max_we, min_we, max_vo, min_vo, max_vi, max_an, min_an
        )

        # load the data with all c-style arrays.
        data, layout = self.gen_data_layout(
            N, edges, sizes, nodes_labels, edges_labels, colors
        )

        fig = go.Figure(data=data, layout=layout)
        pio.write_html(fig, "plot.html", auto_open=True)

    def gen_data_layout(self, N, edges, sizes, nodes_labels, edges_labels, colors):
        """
        This method generates the data containing the coordinates of all nodes
        and their corresponding edges as well as the layout.

        params:
            - N (int): number of nodes
            - edges (list(tuple(int))): list of tuples of indices of nodes.
            - sizes (list(int)): list of sizes of nodes (according to weight).
            - nodes_labels (list(str)): list of descriptions of nodes.
            - edges_labels (list(int)): list of weight of edges.
            - colors (list(str)): list of rgb colors according to attributes.

        returns:
            - data (list(Scatter3d)): list of coordinates and attributes.
            - layout
        """
        G = ig.Graph(edges, directed=False)
        layt = G.layout("kk", dim=3)

        Xn, Yn, Zn = self.gen_xyzn(layt, N)
        Xe, Ye, Ze = self.gen_xyze(layt, edges)

        lines = self.gen_lines(Xe, Ye, Ze, edges_labels)
        markers = self.gen_markers(Xn, Yn, Zn, sizes, nodes_labels, colors)

        layout = self.gen_layout(self.gen_axis())
        data = [lines, markers]

        return data, layout

    def gen_xyzn(self, layt, N):
        """
        Generate 3d vector space with amount of nodes in each coordinate.

        params:
            - layt
            - N (int): amount of nodes.
        returns:
            - Each coordinate.
        """

        Xn = [layt[k][0] for k in range(N)]
        Yn = [layt[k][1] for k in range(N)]
        Zn = [layt[k][2] for k in range(N)]

        return Xn, Yn, Zn

    def gen_xyze(self, layt, edges):
        """
        Create a list of coordinates of the connected nodes by index
        of coordinates of each node.

        params:
            - layt
            - edges (list(tuple(int))): list of edges.

        returns:
            - three list of all the coordinates per axis.
        """

        Xe = []
        Ye = []
        Ze = []

        for e in edges:
            Xe += [layt[e[0]][0], layt[e[1]][0], None]
            Ye += [layt[e[0]][1], layt[e[1]][1], None]
            Ze += [layt[e[0]][2], layt[e[1]][2], None]

        return Xe, Ye, Ze

    def gen_lines(self, Xe, Ye, Ze, edge_labels):
        """
        This method generates the edges of the graph.

        params:
            - Xe (list(int)): list of coordinates of both nodes.
            - Ye
            - Ze
            - edge_labels (list(int)): list of weights per edge.

        returns:
            - edges (Scatter3d): return all coordinates of edges.
        """

        return go.Scatter3d(
            x=Xe,
            y=Ye,
            z=Ze,
            mode="lines",
            line=dict(color="rgb(125, 125, 125)", width=1),
            text=edge_labels,
            hoverinfo="text",
        )

    def gen_markers(self, Xn, Yn, Zn, weights, nodes_labels, colors):
        """
        Generate nodes with colors, sizes and tags.

        params:
            - Xn (list(int)): list of coordinates
            - Yn
            - Zn
            - weights (list(int)): list of size in pixels.
            - nodes_labels (list(str)): list of descriptions.
            - colors (list(str)): list of colors as rgb strings.

        returns:
            - nodes (Scatter3d): all nodes in given coordinates with all
                attributes.
        """

        return go.Scatter3d(
            x=Xn,
            y=Yn,
            z=Zn,
            mode="markers",
            name="tags",
            marker=dict(
                symbol="circle",
                size=weights,
                color=colors,
                colorscale="Viridis",
                line=dict(color="rgb(50,50,50)", width=0.5),
            ),
            text=nodes_labels,
            hoverinfo="text",
        )

    def gen_axis(self):
        """
        Generates an axis which will look the same in each coordinate.

        returns:
            - axis
        """

        return dict(
            showbackground=False,
            showline=False,
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            title="",
        )

    def gen_layout(self, axis):
        """
        Given an axis generate the layout with 3 equal axis, title width and height
        of screen and legend.

        params:
            - axis (dict): dictionary of values.

        returns:
            - layout
        """

        return go.Layout(
            title="Stack Overflow Tags and Their Relations",
            width=1800,
            height=1000,
            showlegend=False,
            scene=dict(
                xaxis=(dict(axis)),
                yaxis=(dict(axis)),
                zaxis=(dict(axis)),
            ),
            margin=dict(t=50),
            hovermode="closest",
        )

    def minmax_weights(self):
        """
        Find min and max weights to normalize size of node in pixels.
        """

        max_weight = max(
            [node.weight for node in self.raw_graph.nodes.values()])
        min_weight = min(
            [node.weight for node in self.raw_graph.nodes.values()])
        return max_weight, min_weight

    def minmax_votes(self):
        """
        Find min and max votes in nodes to normalize in rgb values.
        """

        max_votes = max([node.votes for node in self.raw_graph.nodes.values()])
        min_votes = min([node.votes for node in self.raw_graph.nodes.values()])
        return max_votes, min_votes

    def max_views_answers(self):
        """
        Finds max of views and answers in nodes to normalize in rgb values.
        """

        max_views = max([node.views for node in self.raw_graph.nodes.values()])
        max_answers = max(
            [node.answers for node in self.raw_graph.nodes.values()])
        min_answers = min(
            [node.answers for node in self.raw_graph.nodes.values()])
        return max_views, max_answers, min_answers

    def c_style_arrays(self):
        """
        This method generates c-style arrays of nodes, edges and their labels.
        All indices must correspond to the same node and this step is needed
        since igraph implements graph this way.

        returns:
            - nodes (list(str)): array of names of nodes (tags).
            - edges (list(tuple(int))): list of tuples of indices of nodes.
            - nodes_labels (list(str)): list of descriptions of nodes.
            - edges_labels (list(int)): list of weight of edge.
        """
        nodes = list(self.raw_graph.nodes.keys())

        edges = [
            (nodes.index(n1), nodes.index(n2)) for n1, n2 in self.raw_graph.edges.keys()
        ]

        # Example: Python: 35000 Views: 4500 Answers: 600: Votes: 20
        nodes_labels = [
            "{}: {} Views: {} Answers: {} Votes: {}".format(
                node,
                str(self.raw_graph.nodes[node].weight),
                str(self.raw_graph.nodes[node].views),
                str(self.raw_graph.nodes[node].answers),
                str(self.raw_graph.nodes[node].votes),
            )
            for node in nodes
        ]

        edges_labels = [
            f"{edge[0]} - {edge[1]} - {weight}"
            for edge, weight in self.raw_graph.edges.items()
        ]

        return nodes, edges, nodes_labels, edges_labels

    def attr(self, nodes, max_we, min_we, max_vo, min_vo, max_vi, max_an, min_an):
        """
        This method generates the attributes sizes and colors as c-style arrays.
        Normalizes to weights so there aren't too big nodes (pixels) or too
        small. It also generates the rgb colors where each parameter is red,
        green or blue scaled to fit the values in the dataset.

        paramas:
            - nodes (list(str)): array of node names.
            - max_we (int): max weight in nodes.
            - min_we (int): min weight in nodes.
            - max_vo (int): max votes in nodes.
            - min_vo (int): min votes in nodes.
            - max_vi (int): max views in nodes.
            - max_an (int): max answers in nodes.

        returns:
            - sizes (list(int)): array of normalized weight pro node.
            - colors (list(str)): array of rgb colors reflecting the attributes
                found in each node.
        """
        sizes = [
            (300 - 30) *
            (self.raw_graph.nodes[i].weight - min_we) / (max_we - min_we)
            + 30
            for i in nodes
        ]

        colors = [
            "rgb({}, {}, {})".format(
                0,
                70,
                self.calculate_average_votes_per_view(
                    node, max_vo, min_vo, max_an, min_an
                ),
            )
            for node in self.raw_graph.nodes.values()
        ]
        return sizes, colors

    def calculate_average_votes_per_view(self, node, max_vo, min_vo, max_an, min_an):
        """
        From 0 to 255 create the average of sucessfully answered questions in
        stackoverflow.

        params:
            - node (int): node with all values.
            - max_vo (int): max votes.
            - min_vo (int): min votes.
            - max_an (int): max answers.
            - min_an (int): min answers.

        returns:
            - average 0..255
        """

        return int(255 * node.votes / node.answers)
