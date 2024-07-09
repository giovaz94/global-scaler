import os
import time
import threading
import requests
from components.sys_scaler import SysScaler
from prometheus_api_client import PrometheusConnect


class Guard:

    def __init__(
            self,
            scaler: SysScaler,
            k_big: int,
            k: int,
            sleep: int = 5,
            sampling_counter: int = 10
    ):
        self.guard_thread = None

        self.log_thread = None
        self.k_big = k_big
        self.k = k
        self.sleep = sleep
        self.running = True

        self.request_scaling = False
        self.scaler = scaler

        self.samplings = sampling_counter
        self.__sampling_list = []

        prometheus_service_address = os.environ.get("PROMETHEUS_SERVICE_ADDRESS", "localhost")
        prometheus_service_port = os.environ.get("PROMETHEUS_SERVICE_PORT", "8080")
        prometheus_url = f"http://{prometheus_service_address}:{prometheus_service_port}"
        self.prometheus_instance = PrometheusConnect(url=prometheus_url)

    def start(self) -> None:
        """
        Start the guard process.
        This method will start a new thread that will query the monitor service in order
        to try to check the conditions of the system.

        A second thread will be started to log the metrics of the system.
        """
        self.guard_thread = threading.Thread(target=self.guard)
        self.guard_thread.start()

    def collect_sample(self) -> None:
        """
        Return the inbound workload of the system, 
        querying the external monitoring system.
        """
        query = f"sum(increase(http_requests_total_parser[{self.sleep}s]))"
        try:
            data = self.prometheus_instance.custom_query(query)
            metric_value = float(data[0]['value'][1])
            if metric_value is not None and metric_value > 0:
                self.__sampling_list.append(float(metric_value))
                print(f"Sample collected: {self.__sampling_list}", flush=True)
            else:
                print(f"Value is {metric_value}", flush=True)
                
        except (requests.exceptions.RequestException, KeyError, IndexError) as e:
            print("Error:", e, flush=True)

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
            print("Checking the system...", flush=True)
            self.collect_sample()
            if len(self.__sampling_list) < self.samplings:
                time.sleep(self.sleep)
                continue
            inbound_workload = sum(self.__sampling_list) / (self.sleep * self.samplings)
            self.__sampling_list = []
            print(f"Inbound workload: {inbound_workload}", flush=True)

            current_mcl = self.scaler.get_mcl()
            if self.should_scale(inbound_workload, current_mcl):
                self.scaler.process_request(inbound_workload)
            time.sleep(self.sleep)
