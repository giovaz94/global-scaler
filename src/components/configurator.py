import numpy as np


class Configurator:
    """
    The following class is in charge of calculate the new configuration 
    of the system.

    Arguments
    -----------
    base_config -> a numpy array that stores the base configuration of the system
    mcl_increments -> a numpy array that stores the mcl's increments of the system
    scale_components -> a numpy array that stores the services replicas for each increment
    components_mcl -> a numpy array that stores the mcl of each service
    components_mf -> a numpy array that stores the multiplicative factor of each service
    k_big -> the k_big value
    """
    def __init__(self, base_config ,scale_components, components_mcl, components_mf, k_big: int = 10):
        self._base_config = base_config
        self._scale_components = scale_components
        self._components_mcl = components_mcl
        self._components_mf = components_mf
        self._k_big = k_big

    def calculate_configuration(self, target_workload) -> tuple:
        """
        Calculate the new configuration of the system.
        """
        config = self._base_config.copy()
        deltas = np.zeros(len(self._scale_components))
        mcl = self.extimate_mcl(self._base_config)
        while not self.configuration_found(mcl, target_workload, self._k_big):
            config_found = False
            for i in range(len(self._scale_components)):
                config += self._scale_components[i]
                deltas[i] += 1
                mcl = self.extimate_mcl(config)
                if self.configuration_found(mcl, target_workload, self._k_big):
                    config_found = True
                    break
            if config_found:
                break
        return deltas, mcl

    def configuration_found(self, sys_mcl, target_workload, k_big) -> bool:
        """
        Return true if the configuration is greater than 0
        """
        return sys_mcl - (target_workload + k_big) >= 0
    
    def extimate_mcl(self, deployed_instances) -> int:
        """
        Calculate an extimation of the system's mcl.
        """
        return np.min(deployed_instances * self._components_mcl / self._components_mf)