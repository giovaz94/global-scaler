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
            message_loss = self._execute_prometheus_query("sum(services_message_lost)")
            number_of_instances_deployed = self._execute_prometheus_query("deployed_pods")
            latency = self._execute_prometheus_query(
                "sum(http_response_time_sum) / sum(message_analyzer_complete_message)"
            )

            with open('log.csv', 'a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([iteration * self.sleep, inbound_workload, message_loss, latency, number_of_instances_deployed])
            iteration += 1
            time.sleep(self.sleep)