import yaml
import os
import numpy as np
from kubernetes import client, config
from components.configurator import Configurator
from kubernetes.client.rest import ApiException

class SysScaler:
    """
    SysScaler class will scale the system to a new configuration.
    """
    def __init__(self, configurator: Configurator, starting_mcl: int) -> None:
        self.mcl = starting_mcl
        self.configurator = configurator
        if os.environ.get("INCLUSTER_CONFIG") == "true":
            config.load_incluster_config()
        else:
            config.load_kube_config()
        self.k8s_client = client.CoreV1Api()
        self.total_increment = None

    def get_mcl(self) -> int:
        """
        Return the current mcl of the system.
        """
        return self.mcl
    
    def process_request(self, target_mcl) -> int:
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
        self._apply_increment(increments_to_apply)

        if self.total_increment is None:
            self.total_increment = increments_to_apply
        else:
            self.total_increment += increments_to_apply

        self.mcl = mcl
        return self.mcl

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
            for _ in range(iter_number):
                for file in manifest_files:
                    if num > 0:
                        self._deploy_pod(os.path.join(manifest_path, file))
                    else:
                        with open(os.path.join(manifest_path, file), 'r') as manifest_file:
                            pod_manifest = yaml.safe_load(manifest_file)
                            image_name = pod_manifest["spec"]["containers"][0]["image"]
                            self._delete_pod_by_image(image_name)
    
                
    def _deploy_pod(self, manifest_file_path) -> None:
        """
        Deploy a pod in the cluster.

        Arguments
        -----------
        manifest_file_path -> path to the manifest file to deploy
        """
        try:
            with open(manifest_file_path, 'r') as manifest_file:
                pod_manifest = yaml.safe_load(manifest_file)
                self.k8s_client.create_namespaced_pod(body=pod_manifest, namespace="default")
        except ApiException as e:
            raise Exception(f"Error deploying pod: {e}")

    def _delete_pod_by_image(self, image_name) -> None:
        """
        Delete a pod by image name.
        The deleted pod must be in a healthy state.

        Arguments
        -----------
        image_name -> the image name of the pod to delete
        """
        pods = self.k8s_client.list_pod_for_all_namespaces(watch=False)
        for pod in pods.items:
            if pod.spec.containers[0].image == image_name and pod.status.phase == "Running":
                pod_name = pod.metadata.name
                try:
                    print(f"Deleting pod --> {pod_name}")
                    self.k8s_client.delete_namespaced_pod(name=pod_name, namespace="default")
                    return None
                except Exception as e:
                    print(f"Error deleting poduu '{pod_name}' in namespace default: {e}")
