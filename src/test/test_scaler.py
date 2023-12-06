
import os
import yaml
import pytest
from kubernetes.client.rest import ApiException

@pytest.fixture(autouse=True)
def setup_before_tests(kubernetes_client):
    _delete_all_pods(kubernetes_client)    
    base_manifest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "manifests", "base")
    manifest_files = os.listdir(base_manifest_path)
    for file in manifest_files:
        _deploy_pod(kubernetes_client, os.path.join(base_manifest_path, file))

def test_process_request(setup_before_tests, standard_sys_scaler):
    assert standard_sys_scaler.process_request(80) == 110
    assert standard_sys_scaler.process_request(90) == 110
    assert standard_sys_scaler.process_request(120) == 154

def _deploy_pod(kubernetes_client, manifest_file_path) -> None:
    try:
        with open(manifest_file_path, 'r') as manifest_file:
            pod_manifest = yaml.safe_load(manifest_file)
            kubernetes_client.create_namespaced_pod(body=pod_manifest, namespace="default")
    except ApiException as e:
        raise Exception(f"Error deploying pod: {e}")

def _delete_all_pods(kubernetes_client):
    pods = kubernetes_client.list_pod_for_all_namespaces(watch=False)
    for pod in pods.items:
        pod_name = pod.metadata.name
        try:
            kubernetes_client.delete_namespaced_pod(name=pod_name, namespace="default")
            print(f"Pod '{pod_name}' in namespace default deleted.")
        except Exception as e:
            print(f"Error deleting pod '{pod_name}' in namespace default: {e}")
    
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

