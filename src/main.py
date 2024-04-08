
import numpy as np
import os
from components.configurator import Configurator
from components.sys_scaler import SysScaler
from components.guard import Guard
from prometheus_client import start_http_server


if __name__ == '__main__':

    # Base configuration
    base = np.array([1, 1, 1, 1, 1, 1, 1])

    # Microservices MCL and MF
    microservices_mcl = np.array([70, 80, 181, 181, 40, 40, 250])
    microservices_mf = np.array([1.0, 2.0, 1.5, 1.5, 1.5, 1.5, 1])    

    # Replicas for each increment
    scale_config = np.array([
        [0, 1, 0, 0, 1, 1, 1],  # Increment 1
        [1, 0, 0, 0, 0, 0, 0],  # Increment 2
        [0, 1, 0, 0, 1, 1, 1],  # Increment 3
        [0, 0, 1, 1, 0, 0, 0],  # Increment 4
    ])

    k_big = int(os.environ.get("K_BIG", "10"))
    k = int(os.environ.get("K", "1"))
    sleep = int(os.environ.get("SLEEP", "2"))

    config = Configurator(base, scale_config, microservices_mcl, microservices_mf, k_big)
    scaler = SysScaler(config, 26.6)
    guard = Guard(scaler, k_big, k, sleep)
    guard.start()

    print("Exposing prometheus metrics on port 8000...")
    start_http_server(5000)
