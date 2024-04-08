import time
import threading
import requests
from prometheus_api_client import PrometheusConnect
from src.components.sys_scaler import SysScaler
from src.components.logger import Logger

import os

class Guard:

    def __init__(self, scaler: SysScaler, k_big: int, k: int, sleep: int = 10):
        self.guard_thread = None

        self.log_thread = None
        self.k_big = k_big
        self.k = k
        self.sleep = sleep
        self.running = True

        self.request_scaling = False
        self.scaler = scaler

        prometheus_service_address = os.environ.get("PROMETHEUS_SERVICE_ADDRESS", "localhost")
        prometheus_service_port = os.environ.get("PROMETHEUS_SERVICE_PORT", "8080")
        prometheus_url = f"http://{prometheus_service_address}:{prometheus_service_port}"
        self.prometheus_instance = PrometheusConnect(url=prometheus_url)
        self.logger = Logger(self.prometheus_instance, sleep)
    def start(self) -> None:
        """
        Start the guard process.
        This method will start a new thread that will query the monitor service in order
        to try to check the conditions of the system.

        A second thread will be started to log the metrics of the system.
        """
        self.guard_thread = threading.Thread(target=self.guard)
        self.log_thread = threading.Thread(target=self.logger.log)

        self.guard_thread.start()
        self.log_thread.start()

    def get_inbound_workload(self) -> float:
        """
        Return the inbound workload of the system, 
        querying the external monitoring system.
        """
        query = "rate(http_requests_total_entrypoint[10s])"
        try:
            data = self.prometheus_instance.custom_query(query)
            metric_value = data[0]['value'][1]

            return float(metric_value)
        except (requests.exceptions.RequestException, KeyError, IndexError) as e:
            print("Error:", e)

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
            print(f"Current mcl: {current_mcl}", flush=True)
            print(f"Inbound workload: {inbound_workload}", flush=True)
            if self.should_scale(inbound_workload, current_mcl):
                self.scaler.process_request(inbound_workload)
            time.sleep(self.sleep)
