import pytest
import numpy as np
from components.configurator import Configurator  
from components.sys_scaler import SysScaler

@pytest.fixture()
def standard_configurator():
    """             
    Current system given to the configurator:

    IDX | Service name  | MCL | MF
    ------------------------------ 
    0   Message Parser   110    1
    1   Virus Scanner    120    2
    2   Attachment Man   231    1.5
    3   Image Analyzer   231    1.5
    4   Image Rec         90    1.5
    5   NSFW Detector     90    1.5
    6   Message Analyz   300    1
    """

    # Base configuration
    base = np.array([1, 1, 1, 1, 1, 1, 1])

    # Microservices MCL and MF
    microservices_mcl = np.array([110, 120, 231, 231, 90, 90, 300])
    microservices_mf = np.array([1.0, 2.0, 1.5, 1.5, 1.5, 1.5, 1])    

    # Replicas for each increment
    scale_config = np.array([
        [0, 1, 0, 0, 1, 1, 1],  # Increment 1
        [1, 0, 0, 0, 0, 0, 0],  # Increment 2
        [0, 1, 0, 0, 1, 1, 1],  # Increment 3
        [0, 0, 1, 1, 0, 0, 0],  # Increment 4
    ])

    return Configurator(base, scale_config, microservices_mcl, microservices_mf, k_big=10)

@pytest.fixture
def standard_guard(standard_configurator):
    return SysScaler(60, standard_configurator)