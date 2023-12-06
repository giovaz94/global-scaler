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
        print(f"Actual mcl: {self.mcl}")
        print(f"Target mcl: {target_mcl}")
        print(f"Total increment: {self.total_increment}")

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
        print(f"New mcl: {self.mcl}")
        print(f"New total increment: {self.total_increment}")
        print()

    

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
            for _ in range(int(inc_idx[i])):
                manifest_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "manifests", f"inc_{idx}")
                manifest_files = os.listdir(manifest_path)
                for file in manifest_files:
                    self._deploy_pod(os.path.join(manifest_path, file))

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