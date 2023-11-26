import pytest
from kubernetes import client, config

@pytest.fixture
def kubernetes_client():
    config.load_kube_config()
    return client.CoreV1Api()

def test_list_nodes(kubernetes_client):
    nodes = _list_worker_nodes_name(kubernetes_client)
    assert len(nodes) == 3

def _check_if_pod_deployed_to_node(kubernetes_client, node_name, pod_name):
    pods = kubernetes_client.list_pod_for_all_namespaces(watch=False)
    for pod in pods.items:
        if pod.spec.node_name == node_name and pod.metadata.name == pod_name:
            return True
    return False

def _list_worker_nodes_name(kubernetes_client):
    worker_node_names = []
    nodes = kubernetes_client.list_node().items
    for node in nodes:
        print(node.metadata.labels)
        if node.metadata.labels.get("node-role.kubernetes.io/control-plane") == "true":
            continue
        worker_node_names.append(node.metadata.name)
    return worker_node_names

