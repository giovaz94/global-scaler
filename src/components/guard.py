import pykka

class Guard(pykka.ThreadingActor):
    def __init__(self, k_big: int, k: int, sys_mcl: float) :
        super().__init__()
        self.k_big = k_big
        self.k = k
        self.sys_mcl = sys_mcl
    
    def on_receive(self, message):
        return "Hi, I'm a guard!"
