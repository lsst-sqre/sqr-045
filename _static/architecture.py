"""Source for architecture.png, the architecture diagram."""

import os

from diagrams import Cluster, Diagram
from diagrams.gcp.compute import KubernetesEngine
from diagrams.gcp.network import LoadBalancing
from diagrams.gcp.storage import PersistentDisk
from diagrams.onprem.client import Users
from diagrams.onprem.compute import Server

os.chdir(os.path.dirname(__file__))

graph_attr = {
    "label": "",
}

with Diagram(
        "IDM",
        show=False,
        filename="architecture",
        outformat="png",
        graph_attr=graph_attr,
):
    users = Users("End Users")

    with Cluster("NCSA"):
        cilogon = Server("CILogon")
        comanage = Server("COmanage")
        ldap = Server("LDAP")

        users >> cilogon >> comanage >> ldap
        users >> comanage

    with Cluster("Science Platform"):
        ingress = LoadBalancing("NGINX Ingress")
        notebook = KubernetesEngine("Notebook")
        vo = KubernetesEngine("VO Services")

        redis = KubernetesEngine("Redis")
        storage = PersistentDisk("Redis Storage")

        with Cluster("New Services"):
            control = KubernetesEngine("Account UI")
            tokens = KubernetesEngine("Token Issuer")
            authz = KubernetesEngine("Authorizer")
            quota = KubernetesEngine("Quota Manager")

        log_storage = PersistentDisk("Log Storage")

        users >> ingress >> notebook >> vo
        ingress >> cilogon
        authz << vo
        authz >> redis >> storage
        log_storage >> authz
        authz >> ldap
        ingress >> control >> tokens >> redis >> storage
        control >> quota >> comanage
        control >> comanage
        control << log_storage
