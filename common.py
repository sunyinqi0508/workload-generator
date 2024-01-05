import numpy as np
import pickle
from enum import Enum, auto
from typing import List, Optional

uint32_max = 2 ** 32 - 1
console_log = print

class mode_t(Enum):
    get_distribution = auto()
    generate = auto()
    
class parameters_t:
    def __init__(self):
        self.a1 : float = 1005
        self.a2 : float = 1001
        self.n : int = 100
        self.duration : int= 1000
        self.offset : float = 0
        self.granularity : int = 10
        self.mode : mode_t = mode_t.get_distribution
        self.f : str = './plan.bin'

class dump_t:
    def __init__(self, parameters : Optional[parameters_t] = None, plan : Optional[List[float]] = None):
        self.parameters : parameters_t = parameters
        self.plan : List[float] = plan
