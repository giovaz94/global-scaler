import time
import threading
import requests
from prometheus_api_client import PrometheusConnect
from src.components.sys_scaler import SysScaler
import os


class Guard:

    def __init__(self, scaler: SysScaler, k_big: int, k: int, sleep: int = 10):
        self.guard_thread = None
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

    def get_inbound_workload(self) -> float:
        """
        Return the inbound workload of the system, 
        querying the external monitoring system.
        """
        prometheus_service_address = os.environ.get("PROMETHEUS_SERVICE_ADDRESS", "localhost")
        prometheus_service_port = os.environ.get("PROMETHEUS_SERVICE_PORT", "9090")
        prometheus_url = f"http://{prometheus_service_address}:{prometheus_service_port}"
        query = "rate(http_requests_total_entrypoint[10s])"
        try:
            prom = PrometheusConnect(url=prometheus_url)
            data = prom.custom_query(query)

            metric_value = data[0]['value'][1]  # Assuming there's only one result

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
            print(f"Current mcl: {current_mcl}")
            print(f"Inbound workload: {inbound_workload}")
            if self.should_scale(inbound_workload, current_mcl):
                print("Scaling the system...")
                self.scaler.process_request(inbound_workload)
            time.sleep(self.sleep)
