import numpy as np

class Configurator:
    """
    The following class is in charge of calculate the new configuration 
    of the system.

    Arguments
    -----------
    mcl_increments -> a numpy array that stores the mcl's increments of the system
    scale_components -> a numpy array that stores the services replicas for each increment
    components_mcl -> a numpy array that stores the mcl of each service
    components_mf -> a numpy array that stores the multiplicative factor of each service
    """
    def __init__(self, base_config ,scale_components, components_mcl, components_mf, k_big: int = 10):
        self.base_config = base_config
        self.scale_components = scale_components
        self.components_mcl = components_mcl
        self.components_mf = components_mf
        self.k_big = k_big

    def calculate_configuration(self, target_workload):
        """
        Calculate the new configuration of the system.
        """
        config = np.copy(self.base_config)
        deltas = np.zeros(len(self.scale_components))
        mcl = self.extimate_mcl(self.base_config)
        while not self.configuration_found(mcl, target_workload, self.k_big):
            config_found = False
            for i in range(len(self.scale_components)):
                config += self.scale_components[i]
                deltas[i] += 1
                mcl = self.extimate_mcl(config)
                if self.configuration_found(mcl, target_workload, self.k_big):
                    config_found = True
                    break
            if config_found:
                break
        return deltas

    def configuration_found(self, sys_mcl, target_workload, k_big) -> bool:
        """
        Return true if the configuration is greather than 0
        """
        return sys_mcl - (target_workload + k_big) >= 0
    
    def extimate_mcl(self, deployed_instances):
        """
        Calculate an extimation of the system's mcl.
        """
        return np.min(deployed_instances * self.components_mcl / self.components_mf)