import os

import numpy as np
import pytest
import time

from kubernetes.client.rest import ApiException
from kubernetes import client, config
from src.components.deployment import deploy_pod, delete_pod


@pytest.fixture
def env_configurations():
    return {
        50 : {
            "mcl" : 60,
            "nodes" : {
                "k3d-k3s-default-agent-0": [
                    ("giovaz94/virus-scanner-service:development", 1),
                    ("giovaz94/attachment-manager-service:development", 1),
                    ("giovaz94/image-recognizer-service:development", 1),
                    ("giovaz94/nsfw-detector-service:development", 1),
                ],
                "k3d-k3s-default-agent-1": [
                    ("giovaz94/parser-service:development", 1),
                    ("giovaz94/image-analyzer-service:development", 1),
                    ("giovaz94/message-analyzer-service:development", 1),
                ],
                "k3d-k3s-default-agent-2": []
            },
        },
        80 : {
            "mcl" : 110,
            "nodes" : {
                "k3d-k3s-default-agent-0": [
                    ("giovaz94/virus-scanner-service:development", 1),
                    ("giovaz94/attachment-manager-service:development", 1),
                    ("giovaz94/image-recognizer-service:development", 1),
                    ("giovaz94/nsfw-detector-service:development", 1),
                ],
                "k3d-k3s-default-agent-1": [
                    ("giovaz94/parser-service:development", 1),
                    ("giovaz94/image-analyzer-service:development", 1),
                    ("giovaz94/message-analyzer-service:development", 2),
                    ("giovaz94/image-recognizer-service:development", 1),
                    ("giovaz94/nsfw-detector-service:development", 1),
                ],
                "k3d-k3s-default-agent-2": [
                    ("giovaz94/virus-scanner-service:development", 1),
                ]
            },
        },
        110 : {
            "mcl" : 120,
            "nodes" : {
                "k3d-k3s-default-agent-0": [
                    ("giovaz94/virus-scanner-service:development", 1),
                    ("giovaz94/attachment-manager-service:development", 1),
                    ("giovaz94/image-recognizer-service:development", 1),
                    ("giovaz94/nsfw-detector-service:development", 1),
                ],
                "k3d-k3s-default-agent-1": [
                    ("giovaz94/parser-service:development", 1),
                    ("giovaz94/image-analyzer-service:development", 1),
                    ("giovaz94/message-analyzer-service:development", 2),
                    ("giovaz94/image-recognizer-service:development", 1),
                    ("giovaz94/nsfw-detector-service:development", 1),
                ],
                "k3d-k3s-default-agent-2": [
                    ("giovaz94/virus-scanner-service:development", 1),
                    ("giovaz94/parser-service:development", 1),
                ]
            },
        },
        120 : {
            "mcl" : 154,
            "nodes" : {
                "k3d-k3s-default-agent-0": [
                    ("giovaz94/virus-scanner-service:development", 1),
                    ("giovaz94/attachment-manager-service:development", 1),
                    ("giovaz94/image-recognizer-service:development", 1),
                    ("giovaz94/nsfw-detector-service:development", 1),
                ],
                "k3d-k3s-default-agent-1": [
                    ("giovaz94/parser-service:development", 1),
                    ("giovaz94/image-analyzer-service:development", 1),
                    ("giovaz94/message-analyzer-service:development", 3),
                    ("giovaz94/image-recognizer-service:development", 2),
                    ("giovaz94/nsfw-detector-service:development", 2),
                ],
                "k3d-k3s-default-agent-2": [
                    ("giovaz94/virus-scanner-service:development", 2),
                    ("giovaz94/parser-service:development", 1),
                ]
            },
        },
        154: {
            "mcl": 180,
            "nodes": {
                "k3d-k3s-default-agent-0": [
                    ("giovaz94/virus-scanner-service:development", 1),
                    ("giovaz94/attachment-manager-service:development", 1),
                    ("giovaz94/image-recognizer-service:development", 1),
                    ("giovaz94/nsfw-detector-service:development", 1),
                ],
                "k3d-k3s-default-agent-1": [
                    ("giovaz94/parser-service:development", 1),
                    ("giovaz94/image-analyzer-service:development", 1),
                    ("giovaz94/message-analyzer-service:development", 3),
                    ("giovaz94/image-recognizer-service:development", 2),
                    ("giovaz94/nsfw-detector-service:development", 2),
                ],
                "k3d-k3s-default-agent-2": [
                    ("giovaz94/virus-scanner-service:development", 2),
                    ("giovaz94/parser-service:development", 1),
                    ("giovaz94/attachment-manager-service:development", 1),
                    ("giovaz94/message-analyzer-service:development", 1),
                ]
            },
        },
    }

@pytest.fixture
def kubernetes_client() -> client.ApiClient:
    """
    Return a kubernetes client.
    Before the test, it will deploy the base services.
    After the test, it will clean up all the pods.
    """
    if os.environ.get("INCLUSTER_CONFIG") == "true":
        config.load_incluster_config()
    else:
        config.load_kube_config()
    
    kubernetes_client = client.CoreV1Api()

    # Startup base services
    _startup_base_services(kubernetes_client)

    yield kubernetes_client

    # Cleanup base services
    _delete_all_pods(kubernetes_client)
    return

def _delete_all_pods(client):
   """
   Delete all pods in the default namespace.
   """
   pod_list = client.list_namespaced_pod("default")
   for pod in pod_list.items:
        delete_pod(client, pod.metadata.name, await_deletion=True)

def _startup_base_services(client):
    """
    Deploy the base system's services.
    """
    base_manifest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "manifests", "base")
    manifest_files = os.listdir(base_manifest_path)
    for file in manifest_files:
        try:
            deploy_pod(client, os.path.join(base_manifest_path, file), await_running=True)
        except ApiException as e:
            raise Exception(f"Error deploying pod: {e}")

def _get_status(client):
    """
    Return the status of the system.
    """
    pods = client.list_namespaced_pod("default", watch=False)    
    status = {name: [] for name in [
        node.metadata.name for node in client.list_node().items
        if "node-role.kubernetes.io/control-plane" not in node.metadata.labels
    ]}
    print(status)
    for pod in pods.items:
        image_name = pod.spec.containers[0].image
        found = False
        for i, record in enumerate(status[pod.spec.node_name]):
            if record[0] == image_name:
                found = True
                status[pod.spec.node_name][i] = (record[0], record[1] + 1)
                break
        if not found:
            status[pod.spec.node_name].append((image_name, 1))
    return status

def _check_configuration(kubernetes_client, scaler, current_mcl_request, configuration):
    system_mcl = configuration["mcl"]
    mcl, _ = scaler.process_request(current_mcl_request, await_deployment=True)
    assert mcl == system_mcl
    actual_status = _get_status(kubernetes_client)
    for node_name, expected_pods in configuration["nodes"].items():
        actual_pods = actual_status[node_name]
        assert len(actual_pods) == len(expected_pods)
        for actual_pod in actual_pods:
            assert actual_pod in expected_pods



def test_scale_up(kubernetes_client, standard_sys_scaler, env_configurations):
    for current_mcl_request, configuration in env_configurations.items():
        _check_configuration(kubernetes_client, standard_sys_scaler, current_mcl_request, configuration)
    
def test_scale_down(kubernetes_client, standard_sys_scaler, env_configurations):
    for current_mcl_request, configuration in reversed(env_configurations.items()):
        _check_configuration(kubernetes_client, standard_sys_scaler, current_mcl_request, configuration)

def test_minor_scaling(kubernetes_client, standard_sys_scaler, env_configurations):
    _, increments = standard_sys_scaler.process_request(0, await_deployment=True)
    assert np.equal(increments, np.array([0, 0, 0, 0])).all()

    _, increments = standard_sys_scaler.process_request(88.3, await_deployment=True)
    current_mcl_request = 80
    configuration = env_configurations[current_mcl_request]
    _check_configuration(kubernetes_client, standard_sys_scaler, current_mcl_request, configuration)

    assert np.equal(increments, np.array([1, 0, 0, 0])).all()
    time.sleep(5)

    _, increments = standard_sys_scaler.process_request(77.2, await_deployment=True)
    current_mcl_request = 80
    configuration = env_configurations[current_mcl_request]
    _check_configuration(kubernetes_client, standard_sys_scaler, current_mcl_request, configuration)

    assert np.equal(increments, np.array([0, 0, 0, 0])).all()
    time.sleep(5)

    _, increments = standard_sys_scaler.process_request(67.2, await_deployment=True)
    current_mcl_request = 80
    configuration = env_configurations[current_mcl_request]
    _check_configuration(kubernetes_client, standard_sys_scaler, current_mcl_request, configuration)

    assert np.equal(increments, np.array([0, 0, 0, 0])).all()
    time.sleep(5)

    _, increments = standard_sys_scaler.process_request(0, await_deployment=True)
    current_mcl_request = 50
    configuration = env_configurations[current_mcl_request]
    _check_configuration(kubernetes_client, standard_sys_scaler, current_mcl_request, configuration)

    assert np.equal(increments, np.array([-1, 0, 0, 0])).all()
