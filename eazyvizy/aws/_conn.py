import concurrent.futures
from pyvis.network import Network
from boto3.session import Session
import ipaddr
from botocache.botocache import botocache_context
from eazyvizy._eazyvizy import EazyVizy
from eazyvizy.error import (
    InterruptedError,
    InvalidEazyVizyError,
    EazyVizyError,
    # INVALID_TEMPLE,
    UNKNOWN_ERROR,
    UNKNOWN_ERROR_MSG,
)

class EazyVizyAWS(EazyVizy):
    def __init__(self, session=None):
        super().__init__()
        try:
            self.session = session or Session()
        except BaseException as exc:
            raise InvalidEazyVizyError("Could not initiate AWS connection.") from exc

    def fetch_vpcs(self, region):
        return list(self.session.resource("ec2").vpcs.all())

    def has_route_with_cidr(self, vpc, target_cidr):
        return any(
            r.destination_cidr_block != "local"
            and ipaddr.IPNetwork(target_cidr).overlaps(
                ipaddr.IPNetwork(r.destination_cidr_block)
            )
            for t in vpc.route_tables.all()
            for r in t.routes
        )

    def has_security_group_rule_with_cidr(self, vpc, target_cidr):
        portList = []
        for sg in vpc.security_groups.all():
            for r in sg.ip_permissions:
                for ip_range in r.get("IpRanges", []):
                    if ip_range["CidrIp"] != "0.0.0.0/0":
                        if ipaddr.IPNetwork(ip_range["CidrIp"]).overlaps(
                            ipaddr.IPNetwork(target_cidr)
                        ):
                            if r.get("FromPort"):
                                portList.append(str(r.get("FromPort")))
        return "\n".join([*set(portList)])

    def initialize(self):
        regions = self.session.client("ec2").describe_regions()["Regions"]
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.fetch_vpcs, region) for region in regions]
            for future, region in zip(
                concurrent.futures.as_completed(futures), regions
            ):
                vpcs = future.result()
                edges_to_add = []  # Create an empty list to store the edges
                level = 0
                for vpc in vpcs:
                    node_label = vpc.id
                    for tag in vpc.tags if vpc.tags else []:
                        if tag.get("Key") == "Name":
                            node_label = tag["Value"]
                    # Code to determine node_label based on VPC tags

                    self.add_node(
                        f"{vpc.id}-{level}",
                        node_label,
                        shape="circularImage",
                        image="https://static-00.iconduck.com/assets.00/networkingcontentdelivery-amazonvpc-internetgateway-icon-491x512-g9bp4hsr.png",
                        vpcId=vpc.id,
                        region=region["RegionName"],
                        # level=level,
                    )

                    for other_vpc in vpcs:
                        if vpc.id != other_vpc.id:
                            node_label = other_vpc.id
                            for tag in other_vpc.tags if vpc.tags else []:
                                if tag.get("Key") == "Name":
                                    node_label = tag["Value"]
                            port = self.has_security_group_rule_with_cidr(
                                vpc, other_vpc.cidr_block
                            )
                            has_route = self.has_route_with_cidr(
                                vpc, other_vpc.cidr_block
                            )
                            if has_route or port:
                                self.add_node(
                                    f"{other_vpc.id}-{level}",
                                    node_label,
                                    shape="circularImage",
                                    image="https://static-00.iconduck.com/assets.00/networkingcontentdelivery-amazonvpc-internetgateway-icon-491x512-g9bp4hsr.png",
                                    vpcId=other_vpc.id,
                                    region=region["RegionName"],
                                    # level=level,
                                )

                            if has_route:
                                if port:
                                    # Routing + Security
                                    edges_to_add.append(
                                        {
                                            "source": f"{vpc.id}-{level}",
                                            "target": f"{other_vpc.id}-{level}",
                                            "title": port,
                                            # "color": "blue",
                                            "arrows": {
                                                "to": {
                                                    "enabled": True,
                                                    "scaleFactor": 1,
                                                    "type": "arrow",
                                                },
                                                "middle": {
                                                    "enabled": True,
                                                    "imageHeight": 30,
                                                    "imageWidth": 30,
                                                    "scaleFactor": 1,
                                                    "src": "https://www.cloudoptics.io/wp-content/uploads/2015/03/aws_sg.png",
                                                    "type": "image",
                                                },
                                                "from": {
                                                    "enabled": True,
                                                    "scaleFactor": 1,
                                                    "type": "arrow",
                                                },
                                            },
                                        }
                                    )
                                else:
                                    # Routing Only
                                    edges_to_add.append(
                                        {
                                            "source": f"{vpc.id}-{level}",
                                            "target": f"{other_vpc.id}-{level}",
                                            # "color": "lightblue",
                                            "dashes": True,
                                        }
                                    )
                            else:
                                if port:
                                    # Security Only
                                    edges_to_add.append(
                                        {
                                            "source": f"{vpc.id}-{level}",
                                            "target": f"{other_vpc.id}-{level}",
                                            # "color": "black",
                                            "title": port,
                                            "dashes": True,
                                        }
                                    )

                    level += 1
                # Add all the edges to the graph
                for edge_data in edges_to_add:
                    self.add_edge(
                        edge_data["source"],
                        edge_data["target"],
                        **{
                            k: v
                            for k, v in edge_data.items()
                            if k not in ["source", "target"]
                        }
                    )
