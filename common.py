import numpy as np
import scipy.stats as stats
import pickle
from enum import Enum, auto
from typing import List, Optional
import random

uint32_max = 2 ** 32 - 1
console_log = print

class mode_t(Enum):
    get_distribution = auto()
    generate = auto()
    
class distribution_t:   
    zipf = 0
    normal = 1
    uniform = 2

def truncnorm_01rand(a, n):
    mu = .5 #random.random()
    lower = -mu/a
    upper = (1 - mu)/a
    return stats.truncnorm(lower, upper, mu, a).rvs(n)

distribution_f = {
    distribution_t.zipf: np.random.zipf,
    distribution_t.normal: lambda a, n: truncnorm_01rand(a, n),
    distribution_t.uniform: lambda _, n: np.full(n, 1./n)
}

class parameters_t:
    def __init__(self):
        self.outer = distribution_t.zipf
        self.a1 : float = 1.005
        self.a2 : float = 1.001
        self.n : int = 50000
        self.duration : int = 1000
        self.offset : float = 0
        self.granularity : int = 10
        self.mode : mode_t = mode_t.get_distribution
        self.f : str = './plan.bin'

class dump_t:
    def __init__(self, parameters : Optional[parameters_t] = None, plan : Optional[List[float]] = None):
        self.parameters : parameters_t = parameters
        self.plan : List[float] = plan
