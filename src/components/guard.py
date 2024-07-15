import os
import time
import threading
from components.sys_scaler import SysScaler
from prometheus_api_client import PrometheusConnect


class Guard:

    def __init__(
            self,
            scaler: SysScaler,
            predictions: list[int],
            k_big: int,
            k: int,
            sleep: int = 1,
    ):
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

        self.proactiveness = True #change to an env variable
        self.predictions = predictions

    def start(self) -> None:
        """
        Start the guard process.
        This method will start a new thread that will query the monitor service in order
        to try to check the conditions of the system.

        A second thread will be started to log the metrics of the system.
        """
        self.guard_thread = threading.Thread(target=self.guard)
        self.guard_thread.start()

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
        res =  self.prometheus_instance.custom_query("http_requests_total_parser")
        init_val = float(res[0]['value'][1])
        sl = 1
        iter = 0
        while self.running:
            time.sleep(sl)
            print("Checking the system...", flush=True)
            target_workload = (tot-init_val)/sl
            if iter > 0 and self.proactiveness:
                target_workload = sum(self.predictions[iter-self.sleep:iter])/sl
            print(f"Target workload: {target_workload}", flush=True)
            current_mcl = self.scaler.get_mcl()
            if self.should_scale(target_workload, current_mcl):
                self.scaler.process_request(target_workload)
            res =  self.prometheus_instance.custom_query("http_requests_total_parser")
            tot = float(res[0]['value'][1])
            if tot - init_val > 0:
                init_val = tot
                sl = self.sleep
                iter += sl
            
