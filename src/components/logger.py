import requests
import time
import csv
from prometheus_api_client import PrometheusConnect


class Logger:

    def __init__(self, prometheus_instance: PrometheusConnect, sleep: int = 10):
        self.prometheus_instance = prometheus_instance
        self.sleep = sleep
        self.csv_file = open('log.csv', 'a', newline='')
        self.csv_writer = csv.writer(self.csv_file)

    def _execute_prometheus_query(self, query: str) -> float:
        """
        Execute a query to the Prometheus server.
        """
        try:
            data = self.prometheus_instance.custom_query(query)
            return float(data[0]['value'][1])
        except (requests.exceptions.RequestException, KeyError, IndexError) as e:
            print("Error:", e)

    def log(self) -> None:
        """
        Log the current state of the system saving the metrics in a csv file.
        Metrics are collected from a Prometheus server.
        """
        iteration = 0
        while True:
            inbound_workload = self._execute_prometheus_query("rate(http_requests_total_entrypoint[10s])")
            message_loss = self._execute_prometheus_query("sum(rate(services_message_lost[10s]))")
            complete_message = self._execute_prometheus_query("sum_over_time(message_analyzer_complete_message[10s])")
            number_of_instances_deployed = self._execute_prometheus_query("sum(deployed_pods)")
            latency = self._execute_prometheus_query(
                "topk(1, max by (instance)(clamp_max(sum_over_time(http_response_time_sum[10s]) / sum_over_time(message_analyzer_complete_message[10s]), 999999999)))"
            )

            with open('log.csv', 'a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([iteration * self.sleep, inbound_workload, latency, message_loss, complete_message, number_of_instances_deployed])
            iteration += 1
            time.sleep(self.sleep)