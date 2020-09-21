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
        - G (ig.Graph): Resulting graph to be displayed.
    """

    def __init__(self, mongo_uri, max_tags):
        self.db = self.mongo_setup(mongo_uri)
        self.raw_graph = self.process_data(max_tags)

    def process_data(self, max_tags):
        """
        Create an instance of a custom graph and pre process
        all data available in the mongodb collection.

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
        """

        client = MongoClient(mongo_uri)
        return client["stackoverflowdataset"]

    def create_graph(self):
        N = len(self.raw_graph.nodes)

        nodes = list(self.raw_graph.nodes.keys())
        # max_weight = max([node.weight for node in nodes])
        max_votes = max([node.votes for node in self.raw_graph.nodes.values()])
        min_votes = min([node.votes for node in self.raw_graph.nodes.values()])
        max_views = max([node.views for node in self.raw_graph.nodes.values()])
        max_answers = max(
            [node.answers for node in self.raw_graph.nodes.values()])

        sizes = [self.raw_graph.nodes[i].weight / 10 + 1 for i in nodes]

        edges = [
            (nodes.index(n1), nodes.index(n2)) for n1, n2 in self.raw_graph.edges.keys()
        ]

        nodes_labels = [
            node + ": " + str(self.raw_graph.nodes[node].weight) for node in nodes
        ]

        edges_labels = list(self.raw_graph.edges.values())

        colors = [
            "rgb({}, {}, {})".format(
                int(255 * (node.votes - min_votes) / (max_votes - min_votes)),
                int(node.views / max_views * 255),
                int(node.answers / max_answers * 255),
            )
            for node in self.raw_graph.nodes.values()
        ]

        data, layout = self.gen_data_layout(
            N, edges, sizes, nodes_labels, edges_labels, colors
        )

        fig = go.Figure(data=data, layout=layout)

        pio.write_html(fig, "plot.html", auto_open=True)

    def gen_data_layout(self, N, edges, sizes, nodes_labels, edges_labels, colors):
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
        Xn = [layt[k][0] for k in range(N)]
        Yn = [layt[k][1] for k in range(N)]
        Zn = [layt[k][2] for k in range(N)]

        return Xn, Yn, Zn

    def gen_xyze(self, layt, edges):
        Xe = []
        Ye = []
        Ze = []

        for e in edges:
            Xe += [layt[e[0]][0], layt[e[1]][0], None]
            Ye += [layt[e[0]][1], layt[e[1]][1], None]
            Ze += [layt[e[0]][2], layt[e[1]][2], None]

        return Xe, Ye, Ze

    def gen_lines(self, Xe, Ye, Ze, edge_labels):
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
        return dict(
            showbackground=False,
            showline=False,
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            title="",
        )

    def gen_layout(self, axis):
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
