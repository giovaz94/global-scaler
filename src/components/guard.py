import os
import time
import threading
from components.sys_scaler import SysScaler
from components.mixer import Mixer
from prometheus_api_client import PrometheusConnect


class Guard:

    def __init__(
            self,
            scaler: SysScaler,
            mixer: Mixer,
            predictions,
            k_big = 20,
            k = 10,
            sleep = 10,
    ):
        self.guard_thread = None
        self.log_thread = None
        self.k_big = k_big
        self.k = k
        self.sleep = sleep
        self.running = True

        self.request_scaling = False
        self.scaler = scaler
        self.mixer = mixer

        prometheus_service_address = os.environ.get("PROMETHEUS_SERVICE_ADDRESS", "localhost")
        prometheus_service_port = 61621 #os.environ.get("PROMETHEUS_SERVICE_PORT", "8080")
        prometheus_url = f"http://{prometheus_service_address}:{prometheus_service_port}"
        self.prometheus_instance = PrometheusConnect(url=prometheus_url)

        self.proactiveness = os.environ.get("PROACTIVE", "false").lower() == 'true' #change to an env variable
        self.proactive_reactive = self.proactiveness and os.environ.get("PROACTIVE_REACTIVE", "false").lower() == 'true' 
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
        res = self.prometheus_instance.custom_query("http_requests_total_parser")
        init_val = float(res[0]['value'][1])
        sl = 1
        iter = 0
        last_pred_conf = []
        current_mcl = self.scaler.get_mcl()
        pred_workload = 0
        measured_workload = 0

        if self.proactiveness:
            pred_workload = sum(self.predictions[iter-self.sleep:])/self.sleep
            last_pred_conf = self.scaler.calculate_configuration(pred_workload + self.k_big)
            current_mcl, _ = self.scaler.process_request(last_pred_conf)

        while self.running:
            time.sleep(sl)
            print("Checking the system...", flush=True)
            res = self.prometheus_instance.custom_query("http_requests_total_parser")
            tot = float(res[0]['value'][1])    

            #reactivity
            measured_workload = (tot-init_val)/sl
            target_workload = measured_workload
            if tot - init_val > 0:
                init_val = tot
                sl = self.sleep
                iter += sl    
            
            #proactivity
            if iter > 0 and self.proactiveness:
                pred_workload = sum(self.predictions[iter-self.sleep:iter])/self.sleep
                target_workload = pred_workload
            
            #proactivity + reactivity:
            if iter > 0 and self.proactive_reactive:
                measured_conf = self.scaler.calculate_configuration(measured_workload + self.k_big)
                target_workload = self.mixer.mix(measured_workload, pred_workload, last_pred_conf, measured_conf)
                last_pred_conf = self.scaler.calculate_configuration(pred_workload + self.k_big)
            
            config = self.scaler.get_current_config()
            #TODO: CREATE A LOG FUNCTION AS THE ONE WE DID IN THE ABS SIMULATION!!!!
            print(f"Target workload: {target_workload}, MCL: {current_mcl}, CONFIG: {config}", flush=True)
            if iter > 0 and self.should_scale(target_workload, current_mcl):
                target_conf = self.scaler.calculate_configuration(target_workload + self.k_big)
                current_mcl, _ = self.scaler.process_request(target_conf)      