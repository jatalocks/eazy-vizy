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
import asyncio


def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)

    return wrapped


class EazyVizyAWS(EazyVizy):
    def __init__(self, session=None):
        super().__init__()
        try:
            self.session = session or Session()
        except BaseException as exc:
            raise InvalidEazyVizyError("Could not initiate AWS connection.") from exc

    def fetch_vpcs(self, region):
        return list(self.session.resource("ec2", region_name=region).vpcs.all())

    def has_route_with_cidr(self, vpc, target_cidr):
        return any(
            r.destination_cidr_block != "local"
            and ipaddr.IPNetwork(target_cidr).overlaps(
                ipaddr.IPNetwork(r.destination_cidr_block)
            )
            for t in vpc.route_tables.all()
            for r in t.routes
        )

    def has_security_group_rule_with_cidr(self, vpc, target_vpc):
        portList = []
        for sg in vpc.security_groups.all():
            for r in sg.ip_permissions:
                for ip_range in r.get("IpRanges", []):
                    if ip_range["CidrIp"] != "0.0.0.0/0":
                        if ipaddr.IPNetwork(ip_range["CidrIp"]).overlaps(
                            ipaddr.IPNetwork(target_vpc.cidr_block)
                        ):
                            if r.get("FromPort"):
                                portList.append({"id":sg.id,"port":str(r.get("FromPort"))})
        return portList

    def initialize(self):
        loop = asyncio.get_event_loop()
        for region in self.session.client("ec2").describe_regions()["Regions"]:
            looper = asyncio.gather(
                self.test_vpcs_in_region(
                    self.fetch_vpcs(region["RegionName"]), region["RegionName"]
                )
            )
        loop.run_until_complete(looper)

    @background
    def test_vpcs_in_region(self, vpcs, region):
        level = 0
        for vpc in vpcs:
            edges_to_add = []  # Create an empty list to store the edges
            node_label = vpc.id
            for tag in vpc.tags if vpc.tags else []:
                if tag.get("Key") == "Name":
                    node_label = tag["Value"]
            # Code to determine node_label based on VPC tags
            print(f"Checking VPC {node_label}", "Region", region)

            self.add_node(
                id=f"{vpc.id}-{level}",
                label=node_label,
                shape="circularImage",
                shapeProperties={
                    "size": 30
                },
                image="https://static-00.iconduck.com/assets.00/networkingcontentdelivery-amazonvpc-internetgateway-icon-491x512-g9bp4hsr.png",
                imagePadding=10,
                vpcId=vpc.id,
                region=region,
                # level=level,
            )

            for other_vpc in vpcs:
                if vpc.id != other_vpc.id:
                    node_label = other_vpc.id
                    for tag in other_vpc.tags if vpc.tags else []:
                        if tag.get("Key") == "Name":
                            node_label = tag["Value"]
                    ports = self.has_security_group_rule_with_cidr(
                        vpc, other_vpc
                    )
                    has_route = self.has_route_with_cidr(vpc, other_vpc.cidr_block)
                    if has_route or ports:
                        self.add_node(
                            id=f"{other_vpc.id}-{level}",
                            shapeProperties={
                                "size": 30
                            },
                            label=node_label,
                            shape="circularImage",
                            image="https://static-00.iconduck.com/assets.00/networkingcontentdelivery-amazonvpc-internetgateway-icon-491x512-g9bp4hsr.png",
                            imagePadding=8,
                            vpcId=other_vpc.id,
                            region=region,
                            # level=level,
                        )

                    if has_route:
                        if ports:
                            # Routing + Security
                            for sec in ports:
                                self.add_node(
                                    id=f"{sec['id']}-{level}",
                                    shapeProperties={
                                        "size": 20
                                    },
                                    label=sec['id'],
                                    shape="circularImage",
                                    image="https://www.cloudoptics.io/wp-content/uploads/2015/03/aws_sg.png",
                                    secrutiyGroupId=sec['id'],
                                    region=region,
                                    # level=level,
                                )         
                                if {
                                        "source": f"{vpc.id}-{level}",
                                        "to": f"{sec['id']}-{level}",
                                    } not in edges_to_add:                   
                                    edges_to_add.append(
                                        {
                                            "source": f"{vpc.id}-{level}",
                                            "to": f"{sec['id']}-{level}",
                                        }
                                    )                                
                                edges_to_add.append(
                                    {
                                        "source": f"{sec['id']}-{level}",
                                        "to": f"{other_vpc.id}-{level}",
                                        "label": sec['port'],
                                    }
                                )
                        else:
                            # Routing Only
                            edges_to_add.append(
                                {
                                    "source": f"{vpc.id}-{level}",
                                    "to": f"{other_vpc.id}-{level}",
                                    # "color": "lightblue",
                                    # "dashes": True,
                                }
                            )
                    else:
                        if ports:
                            # Security Only
                            self.add_node(
                                id=f"{sec['id']}-{level}",
                                shapeProperties={
                                    "size": 20
                                },
                                label=sec['id'],
                                shape="circularImage",
                                image="https://www.cloudoptics.io/wp-content/uploads/2015/03/aws_sg.png",
                                secrutiyGroupId=sec['id'],
                                region=region,
                                # level=level,
                            )                                 
                            edges_to_add.append(
                                {
                                    "source": f"{vpc.id}-{level}",
                                    "to": f"{sec['id']}-{level}",
                                    "label": sec['port'],
                                    "dashed": True
                                }
                            )                                
                            edges_to_add.append(
                                {
                                    "source": f"{sec['id']}-{level}",
                                    "to": f"{other_vpc.id}-{level}",
                                    "label": sec['port'],
                                    "dashed": True
                                }
                            )

            # Add all the edges to the graph
            for edge_data in edges_to_add:
                self.add_edge(**edge_data)

            level += 1
