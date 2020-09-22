import unittest
from collections import defaultdict
from graph import *


class TestGraph(unittest.TestCase):
    def test_empty_node(self):
        n = Node()
        self.assertEqual(n.views, 0)
        self.assertEqual(n.votes, 0)
        self.assertEqual(n.answers, 0)
        self.assertEqual(n.weight, 0)

    def test_node_add(self):
        docs = [
            {"views": 10, "answers": 5, "votes": 20},
            {"views": 2, "answers": 5, "votes": 30},
            {"views": 3, "answers": 5, "votes": 50},
        ]

        n = Node()
        for doc in docs:
            n.add(doc)

        self.assertEqual(n.views, 15)
        self.assertEqual(n.votes, 100)
        self.assertEqual(n.answers, 15)
        self.assertEqual(n.weight, 3)

    # def test_empty_graph(self):
    #     g1 = Graph()
    #     self.assertEqual(g1.nodes, defaultdict(Node))
    #     self.assertEqual(g1.edges, defaultdict(int))

    def test_graph_node(self):
        g = Graph()
        n = Node()
        n.add({"views": 10, "answers": 5, "votes": 20})
        g.nodes["test"] = n
        self.assertEqual(g.nodes["test"].views, 10)
        self.assertEqual(g.nodes["test"].answers, 5)
        self.assertEqual(g.nodes["test"].votes, 20)
        self.assertEqual(g.nodes["test"].weight, 1)

    def test_add_document(self):
        g = Graph()
        doc = {
            "tags": ["python", "javascript"],
            "views": 10,
            "votes": 20,
            "answers": 30,
        }
        g.add_document(doc)

        self.assertTrue(g.nodes["python"])
        self.assertTrue(g.nodes["javascript"])

        self.assertTrue(g.edges[("javascript", "python")])
        self.assertFalse(g.edges[("python", "javascript")])

        self.assertEqual(g.edges[("javascript", "python")], 1)

        self.assertEqual(g.nodes["python"].weight,
                         g.nodes["javascript"].weight)
        self.assertEqual(g.nodes["python"].votes, g.nodes["javascript"].votes)
        self.assertEqual(g.nodes["python"].views, g.nodes["javascript"].views)
        self.assertEqual(g.nodes["python"].answers,
                         g.nodes["javascript"].answers)
