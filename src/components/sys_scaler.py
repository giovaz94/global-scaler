import yaml
import os
import numpy as np
from kubernetes import client, config
from components.deployment import deploy_pod, delete_pod_by_image, delete_pod


class SysScaler:
    """
    SysScaler class will scale the system to a new configuration.
    """
    def __init__(self, base_config, scale_components, components_mcl, components_mf) -> None:
        self._base_config = base_config
        self._scale_components = scale_components
        self._components_mcl = components_mcl
        self._components_mf = components_mf
        self.mcl = self.estimate_mcl(base_config)

        if os.environ.get("INCLUSTER_CONFIG") == "true":
            config.load_incluster_config()
        else:
            config.load_kube_config()
        self.k8s_client = client.CoreV1Api()
        self.total_increment = None

    def calculate_configuration(self, target_workload) -> list[int]:
        """
        Calculate the new configuration of the system.
        """
        config = self._base_config.copy()
        deltas = np.zeros(len(self._scale_components))
        mcl = self.estimate_mcl(self._base_config)
        while not self.configuration_found(mcl, target_workload):
            candidate_config = config
            for i in range(len(self._scale_components)):
                candidate_config = config + self._scale_components[i]
                deltas[i] += 1
                mcl = self.estimate_mcl(candidate_config)
                if self.configuration_found(mcl, target_workload):
                    break
            config = candidate_config
        return deltas

    def configuration_found(self, sys_mcl, target_workload) -> bool:
        """
        Return true if the configuration is greater than 0
        """
        return sys_mcl - target_workload >= 0
    
    def estimate_mcl(self, deployed_instances) -> int:
        """
        Calculate an extimation of the system's mcl.
        """
        return np.min((deployed_instances * self._components_mcl) / self._components_mf)
    
    def get_mcl(self) -> float:
        """
        Return the current mcl of the system.
        """
        return self.mcl
    
        
    def get_current_config(self) -> float:
        """
        Return the current configuration of the system.
        """
        return self.total_increment
    
    def process_request(self, deltas, await_deployment=False) -> tuple:
        """
        Process a scaling request.
    
        Arguments
        -----------
        target_mcl -> the target mcl to reach 
        """

        if self.total_increment is None:
            increments_to_apply = deltas
        else:
            increments_to_apply = deltas - self.total_increment
        
        self._apply_increment(increments_to_apply)

        self.total_increment = deltas
        self.mcl = self.estimate_mcl(self.total_increment)
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

            for _ in range(iter_number):
                for file in manifest_files:
                    if num > 0:
                        deploy_pod(self.k8s_client, os.path.join(manifest_path, file), False)
                    else:
                        with open(os.path.join(manifest_path, file), 'r') as manifest_file:
                            pod_manifest = yaml.safe_load(manifest_file)
                            image_name = pod_manifest["spec"]["containers"][0]["image"]
                            node_name = pod_manifest["spec"]["nodeName"]
                            delete_pod_by_image(self.k8s_client, image_name, node_name, False)
