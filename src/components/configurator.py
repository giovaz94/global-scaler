
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
    def __init__(self, scale_components, components_mcl, components_mf):
        self.scale_components = scale_components
        self.components_mcl = components_mcl
        self.components_mf = components_mf

    def calc_scale(target_workload):
        
        pass

    def config_found(self, sys_mcl, inbound_workload, k_big) -> bool:
        """
        Return true if the configuration is greather than 0
        """
        return sys_mcl - (inbound_workload + k_big) >= 0
    
    def extimate_mcl(self, deployed_instances):
        """
        Calculate an extimation of the system's mcl.
        """
        return np.min(deployed_instances * self.components_mcl / self.components_mf)