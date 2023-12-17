import time
import threading
import requests
from components.sys_scaler import SysScaler
import os
import sys
class Guard():

    def __init__(self, scaler: SysScaler, k_big: int, k: int, sleep: int = 10):
        self.k_big = k_big
        self.k = k
        self.sleep = sleep
        self.running = True

        self.request_scaling = False
        self.scaler = scaler

    def start(self) -> None:
        """
        Start the guard process.
        This method will start a new thread that will query the monitor service in order
        to try to check the conditions of the system.
        """
        self.guard_thread = threading.Thread(target=self.guard)
        self.guard_thread.start()

    def stop(self) -> None:
        """
        Stop the guard process.
        """
        self.running = False
        self.guard_thread.join()

    def get_inbound_workload(self) -> int:
        """
        Return the inbound workload of the system, 
        querying the external monitoring system.
        """
        monitor_url = os.environ.get("DB_URL")
        if monitor_url:
            endpoint = monitor_url + "/inboundWorkload"
            response = requests.get(endpoint).json()
            print(f"Inbound workload registered {response['inbound_workload']}")
            return response["inbound_workload"]
        else:
            raise Exception("DB_URL not set")

    def should_scale(self, inbound_workload, current_mcl) -> bool:
        """
        Check the conditions of the system and return True if it should scale.
        """
        return inbound_workload - (current_mcl - self.k_big) > self.k or \
            (current_mcl - self.k_big) - inbound_workload > self.k

    def guard(self) -> None:
        """
        This method is executed in a separate thread.
        Check the conditions of the system and eventually scale it.
        """
        print("Monitoring the system...")
        while self.running:
            inbound_workload = self.get_inbound_workload()
            current_mcl = self.scaler.get_mcl()
            print(f"Current mcl: {current_mcl}")
            print(f"Inbound workload: {inbound_workload}")
            if self.should_scale(inbound_workload, current_mcl):
                print("Scaling the system...")
                self.scaler.process_request(inbound_workload)
            time.sleep(self.sleep)

    def cleanup_actor(self):
        """
        Stop the guard thread and join it.
        """
        if self.guard_thread.is_alive():
            self.running = False
            self.guard_thread.join()
