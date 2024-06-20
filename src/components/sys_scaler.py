import yaml
import os

from kubernetes import client, config
from components.configurator import (Configurator)
from components.deployment import deploy_pod, delete_pod_by_image, delete_pod
import threading


class SysScaler:
    """
    SysScaler class will scale the system to a new configuration.
    """
    def __init__(self, configurator: Configurator, starting_mcl: float) -> None:
        self.mcl = starting_mcl
        self.configurator = configurator
        if os.environ.get("INCLUSTER_CONFIG") == "true":
            config.load_incluster_config()
        else:
            config.load_kube_config()
        self.k8s_client = client.CoreV1Api()
        self.total_increment = None

    def get_mcl(self) -> float:
        """
        Return the current mcl of the system.
        """
        return self.mcl
    
    def process_request(self, target_mcl, await_deployment=False) -> tuple:
        """
        Process a scaling request.
    
        Arguments
        -----------
        target_mcl -> the target mcl to reach 
        """
        deltas, mcl = self.configurator.calculate_configuration(target_mcl)
        if self.total_increment is None:
            increments_to_apply = deltas
        else:
            increments_to_apply = deltas - self.total_increment
        
        print(f"Increments to apply: {increments_to_apply}")
        self._apply_increment(increments_to_apply, await_deployment)

        if self.total_increment is None:
            self.total_increment = increments_to_apply
        else:
            self.total_increment += increments_to_apply

        print(f"Total increments: {self.total_increment}")
        self.mcl = mcl
        return self.mcl, increments_to_apply

    def _apply_increment(self, inc_idx) -> None:
        """
        Apply the configuration to the cluster.

        Arguments
        -----------
        inc_idx -> the increment index to apply
        """
        for i in range(len(inc_idx)):
            if inc_idx[i] == 0:
                continue
            idx = i + 1
            manifest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "manifests", f"inc_{idx}")
            manifest_files = os.listdir(manifest_path)
            num = int(inc_idx[i])
            iter_number = abs(num)

            if num > 0:
                for _ in range(iter_number):
                    files = [os.path.join(manifest_path, file) for file in manifest_files]
                    threading.Thread(target=self.__apply_thread, args=(files,)).start()
            else:
                found_pods = []
                pods = self.k8s_client.list_namespaced_pod("default")

                for _ in range(iter_number):
                    for file in manifest_files:
                        with open(os.path.join(manifest_path, file), 'r') as manifest_file:
                            pod_manifest = yaml.safe_load(manifest_file)
                            image_name = pod_manifest["spec"]["containers"][0]["image"]
                            node_name = pod_manifest["spec"]["nodeName"]
                            try:
                                for pod in pods.items:
                                    found_pod_name = pod.metadata.name
                                    if (pod.spec.containers[0].image == image_name and
                                            pod.spec.node_name == node_name and
                                            found_pod_name not in found_pods and
                                            pod.metadata.name.startswith("sys-pod")):

                                        found_pods.append(found_pod_name)
                            except Exception as e:
                                raise Exception(f"Error deleting pod: {e}")

                            threading.Thread(target=self.__remove_thread, args=(found_pods,)).start()

    def __apply_thread(self, file_list):
        for file in file_list:
            deploy_pod(self.k8s_client, file, False)
        return

    def __remove_thread(self, pod_name_list):
        for pod_name in pod_name_list:
            delete_pod(self.k8s_client, pod_name, False)
        return
