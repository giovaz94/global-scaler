
import numpy as np
import os
from components.configurator import Configurator
from components.sys_scaler import SysScaler
from components.guard import Guard


if __name__ == '__main__':
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
    microservices_mcl = np.array([22, 24, 46.2, 46.2, 18, 18, 60])
    microservices_mf = np.array([1.0, 2.0, 1.5, 1.5, 1.5, 1.5, 5])   

    # Replicas for each increment
    scale_config = np.array([
        [1, 1, 0, 0, 1, 1, 1],  # Increment 1
        [1, 3, 1, 1, 3, 3, 3],  # Increment 2
        [2, 4, 1, 1, 4, 4, 4],  # Increment 3
        [3, 6, 2, 2, 6, 6, 6],  # Increment 4
    ])

    k_big = int(os.environ.get("K_BIG", "2"))
    k = int(os.environ.get("K", "1"))
    sleep = int(os.environ.get("SLEEP", "5"))

    config = Configurator(base, scale_config, microservices_mcl, microservices_mf, k_big)
    scaler = SysScaler(config, 12.0)
    guard = Guard(scaler, k_big, k, sleep)
    guard.start()
