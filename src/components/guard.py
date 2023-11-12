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
        self.system_mcl = self.get_system_mcl()

        self.request_scaling = False

    def on_start(self) -> None:
        self.guard_thread = threading.Thread(target=self.guard)
        self.guard_thread.start()
    
    def on_stop(self) -> None:
        self._cleanup_actor()

    def on_failure(self, exception_type, exception_value, traceback) -> None:
        self._cleanup_actor()
    
    def mark_scaling_as_done(self) -> None:
        """
        Mark the scaling request as done.
        This method is called by the scaler when the scaling is completed.
        """
        self.request_scaling = False
    
    def get_system_mcl(self) -> int:
        """
        Return the actual system MCL
        """
        return 0

    def get_inbound_workload(self) -> int:
        """
        Return the inbound workload of the system, 
        querying the external monitoring system.
        """
        return 0
    
    def should_scale(self) -> bool:
        """
        Check the conditions of the system and return True if it should scale.
        """
        print(self.inbound_workload, self.system_mcl, self.k_big, self.k)
        return self.inbound_workload - (self.system_mcl - self.k_big) > self.k or \
                (self.system_mcl - self.k_big) - self.inbound_workload > self.k

    def guard(self) -> None:
        """
        This method is executed in a separate thread.
        Check the conditions of the system and eventually scale it.
        """
        while self.running:
            # Update variables
            self.inbound_workload = self.get_inbound_workload()
            self.system_mcl = self.get_system_mcl()
            if self.should_scale :
                # Prevent multiple scaling requests
                self.request_scaling = True
                # TODO: send scaling request to the system
            time.sleep(self.sleep)
    
    def _cleanup_actor(self): 
        """
        Stop the guard thread and join it.
        """
        if self.guard_thread.is_alive():
            self.running = False
            self.guard_thread.join()

    
    
