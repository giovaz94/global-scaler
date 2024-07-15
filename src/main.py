
import numpy as np
import os
from components.sys_scaler import SysScaler
from components.guard import Guard
from components.mixer import Mixer


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
        6   Message Analyz   300    2
        """

    # Base configuration
    base = np.array([1, 1, 1, 1, 1, 1, 1])

    # Microservices MCL and MF
    microservices_mcl = np.array([110, 120, 231, 231, 90, 90, 120]) #parser, virus scanner, att manager, image analyzer, image rec, nsfw, mess analyzer 
    microservices_mf = np.array([1.0, 2.0, 1.5, 1.5, 1.5, 1.5, 2])   

    # Replicas for each increment
    scale_config = np.array([
        [1, 1, 0, 0, 1, 1, 1],  # Increment 1
        [1, 3, 1, 1, 3, 3, 3],  # Increment 2
        [2, 4, 1, 1, 4, 4, 4],  # Increment 3
        [3, 6, 2, 2, 6, 6, 6],  # Increment 4
    ])

    #worklod predictions
    predictions = [
                50, 62, 0, 75, 62, 40, 0, 27, 47, 92,
                45, 37, 55, 60, 72, 7, 267, 512, 485, 522,
                520, 522, 512, 540, 575, 570, 575, 632, 620, 630,
                617, 610, 577, 600, 592, 555, 550, 570, 567, 562,
                562, 562, 550, 537, 537, 552, 565, 580, 640, 665,
                665, 737, 725, 722, 735, 725, 695, 732, 737, 732,
                715, 690, 712, 707, 710, 695, 697, 730, 722, 727,
                670, 572, 585, 580, 580, 575, 540, 525, 522, 520,
                517, 525, 502, 507, 507, 507, 500, 500, 500, 487,
                500, 470, 455, 427, 427, 420, 407, 400, 400, 392,
                425, 430, 397, 367, 365, 337, 315, 325, 332, 322,
                312, 315, 317, 315, 312, 317, 292, 280, 282, 272,
                272, 275, 287, 305, 305, 297, 305, 317, 330, 320,
                312, 325, 322, 320, 312, 327, 310, 300, 280, 262,
                262, 257, 252, 252, 247, 260, 240, 230, 220, 230,
                222, 232, 217, 217, 190, 190, 180, 175, 175, 175,
                187, 115, 97, 82, 82, 65, 55, 35, 80, 77,
                92, 140, 150, 37, 117, 82, 155, 147, 262, 395,
                402, 437, 430, 447, 437, 452, 475, 480, 442, 402,
                25, 2, 12, 32, 2, 0, 10, 20, 0, 25
    ]

    k_big = int(os.environ.get("K_BIG", "20"))
    k = int(os.environ.get("K", "10"))
    sleep = int(os.environ.get("SLEEP", "10")) #it will be automatically adjusted to 10s as soon the simulation starts 
    mixer = Mixer()
    scaler = SysScaler(base, scale_config, microservices_mcl, microservices_mf)
    guard = Guard(scaler, mixer, predictions, k_big, k, sleep)
    guard.start()
