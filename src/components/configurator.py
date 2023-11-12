
import numpy as np
from numpy import ndarray as NDArray

class Configurator:
    """
    The following class is in charge of calculate the new configuration 
    of the system.

    Arguments
    -----------
    mcl_increments -> a numpy array that stores the mcl's increments of the system
    scale_components -> a numpy array that stores the services replicas for each increment

    """
    def __init__(self, mcl_increments, scale_components):
        self.mcl_increments = mcl_increments
        self.scale_components = scale_components

    def scale():
        pass


    def _config_fond() -> bool:
        """
        Return true if a ne configuration is found
        """
        pass