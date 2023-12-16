import yaml
import os
import sys
from kubernetes import client, config
from components.configurator import Configurator
from components.deployment import deploy_pod, delete_pod_by_image

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
    
    def process_request(self, target_mcl) -> tuple:
        """
        Process a scaling request.
    
        Arguments
        -----------
        target_mcl -> the target mcl to reach 
        """
        deltas, mcl = self.configurator.calculate_configuration(target_mcl)
        if self.total_increment is None:
            print(f"Qui")
            increments_to_apply = deltas
        else:
            increments_to_apply = deltas - self.total_increment
        
        print(f"Increments to apply: {increments_to_apply}")
        sys.stdout.flush()
        self._apply_increment(increments_to_apply)

        if self.total_increment is None:
            self.total_increment = increments_to_apply
        else:
            self.total_increment += increments_to_apply

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
            for _ in range(iter_number):
                for file in manifest_files:
                    if num > 0:
                        deploy_pod(self.k8s_client, os.path.join(manifest_path, file))
                    else:
                        with open(os.path.join(manifest_path, file), 'r') as manifest_file:
                            pod_manifest = yaml.safe_load(manifest_file)
                            image_name = pod_manifest["spec"]["containers"][0]["image"]
                            node_name = pod_manifest["spec"]["nodeName"]
                            delete_pod_by_image(self.k8s_client, image_name, node_name)
    