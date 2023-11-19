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

def test_configuration(standard_system):
    assert np.equal(standard_system.calculate_configuration(50)[0], np.array([0, 0, 0, 0])).all()
    assert np.equal(standard_system.calculate_configuration(80)[0], np.array([1, 0, 0, 0])).all()
    assert np.equal(standard_system.calculate_configuration(110)[0], np.array([1, 1, 0, 0])).all()
    assert np.equal(standard_system.calculate_configuration(120)[0], np.array([1, 1, 1, 0])).all()
    assert np.equal(standard_system.calculate_configuration(154)[0], np.array([1, 1, 1, 1])).all()

    # Etc ..... 
    assert np.equal(standard_system.calculate_configuration(180)[0], np.array([2, 1, 1, 1])).all()
    assert np.equal(standard_system.calculate_configuration(220)[0], np.array([2, 2, 1, 1])).all()
    assert np.equal(standard_system.calculate_configuration(250)[0], np.array([2, 2, 2, 1])).all()




