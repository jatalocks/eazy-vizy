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
                # print(
                #     r.destination_cidr_block,
                #     r.transit_gateway_id,
                #     r.vpc_peering_connection_id,
                # )
                type = "Direct"
                if r.transit_gateway_id:
                    type = "TGW"
                if r.vpc_peering_connection_id:
                    type = "Peering"
                if r.destination_cidr_block != "local" and ipaddr.IPNetwork(
                    target_cidr
                ).overlaps(ipaddr.IPNetwork(r.destination_cidr_block)):
                    routeList.append({"id": t.id,"type":type,"assoc_id":r.transit_gateway_id or r.vpc_peering_connection_id or ""})
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


    def add_vpc(self, vpc, region):
        vpc_metadata = {"shape": "circularImage", "vpcId": vpc.id, "region": region}
        node_label = vpc.id
        if vpc.tags:
            for tag in vpc.tags:
                if tag.get("Key") == "Name":
                    node_label = tag["Value"]
                    break
        self.add_node(id=vpc.id, label=node_label, 
        image="https://static-00.iconduck.com/assets.00/networkingcontentdelivery-amazonvpc-internetgateway-icon-491x512-g9bp4hsr.png", 
        **vpc_metadata, size=30, scaling={"min": 30, "max": 30})
    
    def add_route_table(self, rtable,vpc, region):
        vpc_metadata = {"shape": "circularImage", "vpcId": vpc.id, "region": region}
        self.add_node(id=rtable["id"], label=rtable["id"], 
        image="https://symbols.getvecta.com/stencil_20/8_customer-gateway.5f8e151d08.jpg", 
        **vpc_metadata, size=15, scaling={"min": 15, "max": 15})

    def add_tgw(self, tgw, region):
        vpc_metadata = {"shape": "circularImage", "region": region}
        self.add_node(id=tgw, label=tgw, 
        image="https://global-uploads.webflow.com/5f05d5858fab461d0d08eaeb/635a593ae410e66d0c8b8b00_transit_gateway_light.svg", 
        **vpc_metadata, size=15, scaling={"min": 15, "max": 15})

    def add_peering(self, add_peering, region):
        vpc_metadata = {"shape": "circularImage", "region": region}
        self.add_node(id=add_peering, label=add_peering, 
        image="https://symbols.getvecta.com/stencil_9/28_vpc-peering.735192d824.svg", 
        **vpc_metadata, size=15, scaling={"min": 15, "max": 15})

    def add_aws_edge(self, source, target, color, dashed, ports):
        if ports:
            self.add_edge(**{
                "source": source, 
                "to": target, 
                "title": str(ports), 
                "arrows": {"to": {"enabled": True, "scaleFactor": 1, "type": "arrow"}, "middle": {"enabled": True, "imageHeight": 30, "imageWidth": 30, "scaleFactor": 1, "src": "https://www.cloudoptics.io/wp-content/uploads/2015/03/aws_sg.png", "type": "image"}, "from": {"enabled": True, "scaleFactor": 1, "type": "arrow"}}, 
                "dashed": dashed, 
                "color": color
            })
        else:
            self.add_edge(**{
                "source": source, 
                "to": target, 
                "dashed": dashed, 
                "color": color
            })

    @background
    def test_vpcs_in_region(self, vpcs, region):
        r = lambda: random.randint(0, 255)
        for vpc in vpcs:
            color = "#%02X%02X%02X" % (r(), r(), r())
            self.add_vpc(vpc, region)
            for other_vpc in vpcs:
                if vpc.id != other_vpc.id:
                    self.add_vpc(other_vpc, region)
                    ports = self.has_security_group_rule_with_cidr(vpc, other_vpc)
                    has_route = self.has_route_with_cidr(vpc, other_vpc.cidr_block)
                    if has_route:
                        for rtable in has_route:
                            self.add_route_table(rtable,vpc,region)
                            if rtable['type'] == 'TGW':
                                self.add_tgw(rtable['assoc_id'],region)
                                self.add_aws_edge(rtable['id'],rtable['assoc_id'],color,dashed=False,ports=ports)
                                self.add_aws_edge(rtable['assoc_id'],other_vpc.id,color,dashed=False,ports=ports)
                            elif rtable['type'] == 'Peering':
                                self.add_peering(rtable['assoc_id'],region)
                                self.add_aws_edge(vpc.id,rtable["id"],color,dashed=False,ports=ports)
                                self.add_aws_edge(rtable["id"],other_vpc.id,color,dashed=False,ports=ports)
                            else:
                                self.add_aws_edge(vpc.id,rtable['id'],color,dashed=False,ports=ports)
                                self.add_aws_edge(rtable['id'],other_vpc.id,color,dashed=False,ports=ports)
                    elif ports:
                        self.add_aws_edge(vpc.id,other_vpc.id,color,dashed=True,ports=ports)
