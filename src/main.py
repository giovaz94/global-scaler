
import numpy as np
from components.configurator import Configurator
from components.sys_scaler import SysScaler
from components.guard import Guard

if __name__ == '__main__':

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

    k_big = 10
    k = 1

    config = Configurator(base, scale_config, microservices_mcl, microservices_mf, k_big)
    scaler = SysScaler(60, config)
    guard = Guard(scaler, k_big, k)
    guard.start()


