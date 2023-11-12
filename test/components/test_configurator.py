import pytest
import os
import sys
import numpy as np

# Path to the src folder
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from components.configurator import Configurator  # NOQA

@pytest.fixture()
def standard_system():
    """             
    Current system given to the configurator:

                    MCL    MF 
    Message Parser: 110    1
    Virus Scanner : 120    2
    Attachment Man: 231    1.5
    Image Analyzer: 231    1.5
    Image Rec     :  90    1.5
    NSFW Detector :  90    1.5
    Message Analyz: 300    1
    """
    microservices_mcl = np.array([110, 120, 231, 231, 90, 90, 300])
    microservices_mf = np.array([1.0, 2.0, 1.5, 1.5, 1.5, 1.5, 1])    

    # Replicas for each increment
    replicas = np.array([
        [0, 1, 0, 0, 1, 1, 1],  # Increment 1
        [1, 0, 0, 0, 0, 0, 0],  # Increment 2
        [0, 1, 0, 0, 1, 1, 1],  # Increment 3
        [0, 0, 1, 1, 0, 0, 0],  # Increment 4
    ])

    return Configurator(replicas, microservices_mcl, microservices_mf)

def test_extimate_mcl(standard_system):
    base = np.array([1, 1, 1, 1, 1, 1, 1])
    assert standard_system.extimate_mcl(base) == 60

    config_1 = base + np.array([0, 1, 0, 0, 1, 1, 1])
    assert standard_system.extimate_mcl(config_1) == 110

    config_2 = config_1 + np.array([1, 0, 0, 0, 0, 0, 0])
    assert standard_system.extimate_mcl(config_2) == 120

    config_3 = config_2 + np.array([0, 1, 0, 0, 1, 1, 1])
    assert standard_system.extimate_mcl(config_3) == 154

    config_4 = config_3 + np.array([0, 0, 1, 1, 0, 0, 0])
    assert standard_system.extimate_mcl(config_4) == 180


