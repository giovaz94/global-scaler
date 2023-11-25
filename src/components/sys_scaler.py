import yaml
from kubernetes import client, config
from components.configurator import Configurator
from kubernetes.client.rest import ApiException

class SysScaler:
    """
    SysScaler class will scale the system to a new configuration.
    """
    def __init__(self, starting_mcl: int, configurator: Configurator) -> None:
        self.mcl = starting_mcl
        self.configurator = configurator
    
        config.load_incluster_config()
        self.k8s_client = client.CoreV1Api()

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
        config = self.configurator.calculate_configuration(target_mcl)

        # TODO: Apply the configuration
        self.mcl = self.apply_configuration(config)

        # TODO: Return the new mcl 
        return self.mcl

    def apply_configuration(self, configuration_file) -> None:
        """
        Apply the new configuration.

        Arguments
        -----------
        configuration_file -> configuration to apply in the system
        """
        
        pass

    def deploy_pod(self, manifest_file_path) -> bool:
        """
        Deploy a pod in the cluster.

        Arguments
        -----------
        manifest_file_path -> path to the manifest file to deploy
        """
        try:
            with open(manifest_file_path, 'r') as manifest_file:
                pod_manifest = yaml.safe_load(manifest_file)
            api_response = self.k8s_client.create_namespaced_pod( body=pod_manifest, namespace="default")
            print("Pod created. status='%s'" % str(api_response.status))
            return True
        except ApiException as e:
            raise Exception(f"Error deploying pod: {e}")