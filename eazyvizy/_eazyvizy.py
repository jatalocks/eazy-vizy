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
                "filter": "physics, layout",
                "showButton": True,
            },
            "edges": {"smooth": False},
            "node": {"physics": False},
            "physics": {
                "barnesHut": {
                    "centralGravity": 0.2,
                    "springLength": 115,
                    "avoidOverlap": 1,
                },
                "minVelocity": 0.75,
            },
        }

    def add_node(self, **kwargs):
        print("Adding Node")
        id = kwargs.pop("id")
        self.graph.add_node(id, **kwargs)

    def add_edge(self, **kwargs):
        print("Adding Edge")
        self.graph.add_edge(**kwargs)

    def get_options(self):
        return str(self.options)

    def set_option(self, key, value):
        self.options[key] = value

    def convert_options_to_dict(self):
        return self.options

    def generate_html(self, name="example.html"):
        self.graph.set_options(self.get_options())
        self.graph.show(name)
