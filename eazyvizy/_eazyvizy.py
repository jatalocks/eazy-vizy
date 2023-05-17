from pyvis.network import Network
import json
import boto3
from .logger import ConsoleLogger


class EazyVizy:
    logger = ConsoleLogger()
    graph = Network(directed=True, filter_menu=True)

    def __init__(self):
        self.options = {
            "configure": {
                "enabled": True,
                "filter": "physics, edges",
                "showButton": True,
            },
            "edges": {"smooth": False},
            # "node": {"physics": False},
            "physics": {
                "hierarchicalRepulsion": {
                    "springLength": 235,
                    "springConstant": 0.1,
                    "nodeDistance": 100,
                    "damping": 0.3,
                    "avoidOverlap": 1,
                },
                "minVelocity": 0.75,
                "solver": "hierarchicalRepulsion",
            },
        }

    def add_node(self, **kwargs):
        id = kwargs.pop("id")
        self.graph.add_node(id, **kwargs)

    def add_edge(self, **kwargs):
        self.graph.add_edge(**kwargs)

    def add_edges(self, edges):
        for edge in edges:
            self.graph.add_edge(**edge)

    def get_options(self):
        return json.dumps(self.options)

    def set_option(self, key, value):
        self.options[key] = value

    def convert_options_to_dict(self):
        return self.options

    def generate_html(self, name="example.html"):
        self.graph.set_options(self.get_options())
        self.graph.show(name)
