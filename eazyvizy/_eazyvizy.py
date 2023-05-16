from pyvis.network import Network
import json
import boto3
from .logger import ConsoleLogger
class EazyVizy:
    logger = ConsoleLogger()

    def __init__(self):
        self.graph = Network(directed=True, filter_menu=True)
        self.options = {
            "configure": {
                "enabled": True,
                "filter": "physics, layout",
                "showButton": True
            },
            "edges": {
                "smooth": False
            },
            "node": {
                "physics": False
            },
            "physics": {
                "barnesHut": {
                    "centralGravity": 0.15,
                    "springLength": 115,
                    "avoidOverlap": 1
                },
                "minVelocity": 0.75
            }
        }

    def add_node(self, node_id, node_label, **kwargs):
        self.logger.color("Adding Node","blue")
        self.graph.add_node(node_id, node_label, **kwargs)

    def add_edge(self, source, target, **kwargs):
        self.logger.color("Adding Edge","green")
        self.graph.add_edge(source, target, **kwargs)

    def get_options(self):
        return json.dumps(self.options)

    def set_option(self, key, value):
        self.options[key] = value

    def convert_options_to_dict(self):
        return self.options

    def generate_html(self, name="example.html"):
        self.graph.show(name)