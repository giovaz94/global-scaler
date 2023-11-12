import time
import threading
from pykka import ThreadingActor
class Guard(ThreadingActor):
   
    def __init__(self, k_big: int, k: int, sleep: int = 10):
        super().__init__()
        self.k_big = k_big
        self.k = k
        self.sleep = sleep
        
        self.running = True

        self.inbound_workload = 0
        self.system_mcl = self._get_system_mcl()

        self.request_scaling = False

    def on_receive(self, message):
        print("Guard received: " + message)
        return "Guard response"
    
    def on_start(self):
        self.guard_thread = threading.Thread(target=self.guard)
        self.guard_thread.start()
    
    def on_stop(self):
        self._cleanup_actor()

    def on_failure(self, exception_type, exception_value, traceback):
        self._cleanup_actor()

    def guard(self):
        """
        This method is executed in a separate thread.
        Check the conditions of the system and eventually scale it.
        """
        while self.running:
            self.inbound_workload = self._get_inbound_workload()
            if(self.inbound_workload - (self.system_mcl - self.k_big) > self.k or
               (self.system_mcl - self.k_big) - self.inbound_workload > self.k):
                # Prevent multiple scaling requests
                self.request_scaling = True
                # TODO: send scaling request to the system
                print("Scale up/down")
            time.sleep(self.sleep)

    def _get_system_mcl(self):
        """
        Return the actual system MCL
        """
        return 0

    def _get_inbound_workload(self):
        """
        Return the inbound workload of the system, 
        querying the external monitoring system.
        """
        return 0
    
    def _cleanup_actor(self): 
        """
        Stop the guard thread and join it.
        """
        if self.guard_thread.is_alive():
            self.running = False
            self.guard_thread.join()

    
    
