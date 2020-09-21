from dataclasses import dataclass
from collections import defaultdict
import itertools


@dataclass
class Node:
    """
    Node represents a node in a graph. It contains the values read from
    all documents in collection about each tag.

    attr:
        - views (int): total of views.
        - answers (int): total of answers.
        - votes (int): total of votes (positive + negative).
        - weight (int): total number of times it appears in all questions.

    """

    views: int = 0
    answers: int = 0
    votes: int = 0
    weight: int = 0

    def add(self, doc):
        """
        add method appends values related to the tag (represented by node).

        params:
            - doc (dict): mongodb document with numbers of views,
                answers, votes and list of tags.

        """

        self.views += doc["views"]
        self.answers += doc["answers"]
        self.votes += doc["votes"]
        self.weight += 1


@dataclass
class Graph:
    """
    Graph is a raw representation of how the data scrapped and saved in the
    database should be constructed using the igraph library and represented
    by plotly.

    attr:
        - nodes (Dict[str, Node]): Each node is a name of a tag in a
            stackoverflow question and the total of views, answers, votes
            and times it was used.
        - edges (Dict[Tuple(str, str), int]): Each edge represents two
            strings for each of the tag (Node) and the amount of
            times they were used together.
    """

    nodes = defaultdict(Node)
    edges = defaultdict(int)

    def add_document(self, doc):
        """
        add_document appends all values per document about each tag in document
        (question) and increments the weight on each edge.

        params:
            - doc (dict): mongodb document with numbers of views,
                answers, votes and list of tags.
        """

        for tag in doc["tags"]:
            self.nodes[tag].add(doc)

        for edge in set(itertools.combinations(doc["tags"], 2)):
            # make sure no two tuples are created for the same tags
            # because of the order.
            self.edges[tuple(sorted(edge))] += 1
