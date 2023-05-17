from pyvis.network import Network
from boto3.session import Session
import ipaddr
import random
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
        routeList = []
        for t in vpc.route_tables.all():
            for r in t.routes:
                print(
                    r.destination_cidr_block,
                    r.transit_gateway_id,
                    r.vpc_peering_connection_id,
                )
                if r.destination_cidr_block != "local" and ipaddr.IPNetwork(
                    target_cidr
                ).overlaps(ipaddr.IPNetwork(r.destination_cidr_block)):
                    routeList.append({"id": t.id})
        return routeList

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
                                portList.append(
                                    {"id": sg.id, "port": str(r.get("FromPort"))}
                                )
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
        r = lambda: random.randint(0,255)
        for vpc in vpcs:
            color = '#%02X%02X%02X' % (r(),r(),r())

            vpc_metadata = {
                "shape": "circularImage",
                "vpcId": vpc.id,
                "region": region,
            }

            node_label = next(
                (tag["Value"] for tag in vpc.tags if tag.get("Key") == "Name"), vpc.id
            )
            print(f"Checking VPC {node_label}", "Region", region)
            self.add_node(
                id=vpc.id,
                label=node_label,
                image="https://static-00.iconduck.com/assets.00/networkingcontentdelivery-amazonvpc-internetgateway-icon-491x512-g9bp4hsr.png",
                **vpc_metadata,
                size=40
            )

            for other_vpc in vpcs:
                other_vpc_metadata = {
                    "shape": "circularImage",
                    "vpcId": other_vpc.id,
                    "region": region,
                    "size": 40
                }
                if vpc.id != other_vpc.id:
                    node_label = next(
                        (
                            tag.get("Value")
                            for tag in other_vpc.tags
                            if tag.get("Key") == "Name"
                        ),
                        other_vpc.id,
                    )
                    ports = self.has_security_group_rule_with_cidr(vpc, other_vpc)

                    for sec in ports:
                        self.add_node(
                            id=sec["id"],
                            label=sec["id"],
                            image="https://www.cloudoptics.io/wp-content/uploads/2015/03/aws_sg.png",
                            secrutiyGroupId=sec["id"],
                            **vpc_metadata,
                            size=10
                        )


                    has_route = self.has_route_with_cidr(vpc, other_vpc.cidr_block)

                    self.add_node(
                        id=other_vpc.id,
                        label=node_label,
                        image="https://static-00.iconduck.com/assets.00/networkingcontentdelivery-amazonvpc-internetgateway-icon-491x512-g9bp4hsr.png",
                        **other_vpc_metadata,
                    )
                    if has_route:
                        for rtable in has_route:
                            self.add_node(
                                id=rtable['id'],
                                label=rtable['id'],
                                image="data:image/png;base64,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",
                                **vpc_metadata,
                                size=10
                            )

                        if not ports:
                            self.add_edges(
                                [
                                    {
                                        "source": vpc.id,
                                        "to": rtable['id'],
                                        "title": sec["port"],
                                        "color": color
                                    },
                                    {
                                        "source": rtable['id'],
                                        "to": other_vpc.id,
                                        "title": sec["port"],
                                        "color": color
                                    },
                                ]
                            )
                        else:
                            for sec in ports:
                                self.add_edges(
                                    [
                                        {
                                            "source": vpc.id,
                                            "to": sec["id"],
                                            "title": sec["port"],
                                            "color": color
                                        },
                                        {
                                            "source": sec["id"],
                                            "to": rtable['id'],
                                            "title": sec["port"],
                                            "color": color
                                        },
                                        {
                                            "source": rtable['id'],
                                            "to": other_vpc.id,
                                            "title": sec["port"],
                                            "color": color
                                        },
                                    ]
                                )
                    else:
                        for sec in ports:
                            self.add_edges(
                                [
                                    {
                                        "source": vpc.id,
                                        "to": sec["id"],
                                        "title": sec["port"],
                                        "dashed": has_route is False,
                                        "color": color
                                        
                                    },
                                    {
                                        "source": sec["id"],
                                        "to": other_vpc.id,
                                        "title": sec["port"],
                                        "dashed": has_route is False,
                                        "color": color
                                    },
                                ]
                            )
