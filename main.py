from common import *
        
import time
import random
from collections.abc import Iterable, Callable

help_str = '''Parameters:
  a1: (outer/low-pass) skewness, 
  a2: (inner/high-pass) skewness, 
  n: number of samples
  duration: range of samples (in seconds)
  offset: offset of samples (delay in seconds)
  f: save/load file location (default: ./plan.bin)
  mode: 
       get_distribution: get and save the distribution
       generate: generate queries based on the distribution
'''


parameters = parameters_t()
plan = None
n_threads = None

def init(seed = 1):
    random.seed(time.time() + seed)
    np.random.seed(int(random.random() * time.perf_counter_ns()) % uint32_max)
    random.seed(int(np.random.random() * time.perf_counter_ns()))

def gen_distribution():
    global plan
    def get_normalized_zipf(a, n, r, accumulate = np.add.accumulate):
        if n == 0: return np.empty(0)
        data = np.random.zipf(a, n).astype(np.float64)
        data /= np.sum(data)
        accumulate(data, out = data)
        data *= r
        return data
    
    weights = get_normalized_zipf(parameters.a1, parameters.granularity, parameters.duration, lambda x, **_: x)
    np.random.shuffle(weights)
    weights = np.round(weights).astype(np.int32)
    weights[-1] = max(parameters.n - np.sum(weights[:-1]), 0)
    offsets = (np.array(range(0, parameters.granularity), dtype=np.float64)/parameters.granularity) * parameters.duration
    duration_per_segment = parameters.duration / parameters.granularity
    plan = [k for w, off in zip(weights, offsets) for k in get_normalized_zipf(parameters.a2, w, duration_per_segment) + off]
    with open(parameters.f, 'wb') as fp:
        pickle.dump(dump_t(parameters, plan), fp)

def generate_impl(workload : Iterable[Callable]): # submit workload functions as a list of functions
    time.sleep(parameters.offset) # sleep off the offset
    t0 = time.perf_counter()
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        while len(plan) > 0:
            t = plan.pop(0)
            while t > time.perf_counter() - t0:
                if t < time.perf_counter() - t0 + .03: # python's sleep is not accurate enough
                    while t > time.perf_counter() - t0: # when delta_t < epsilon, busy wait
                        continue
                    else:
                        executor.submit(workload.pop(0), t) # submit the workload precisely at time t.
                        break
                else: 
                    time.sleep(t - (time.perf_counter() - t0) - .03)

def generate(workload : Iterable[Callable], plan_path: str):
    with open(plan_path, 'rb') as fp:
        dump : Optional[dump_t] = pickle.load(fp)
        global plan, parameters
        plan = dump.plan
        parameters = dump.parameters
        generate_impl(workload)
        
def main():
    import sys, copy
    argv = copy.deepcopy(sys.argv)
    global parameters
    
    print_help = False
    argv.pop(0)
    while len(argv) > 0:
        arg = argv.pop(0)
        match arg.lower().strip():
            case '-a1' | '--a1':
                try: parameters.a1 = float(argv.pop(0))
                except Exception as e: print(e)
            case '-a2' | '--a2':
                try: parameters.a2 = float(argv.pop(0))
                except Exception as e: print(e)
            case '-n' | '--n':
                try: parameters.n = int(argv.pop(0))
                except Exception as e: print(e)
            case '-d' | '--duration':
                try: parameters.duration = int(argv.pop(0))
                except Exception as e: print(e)
            case '-o' | '--offset': 
                try: parameters.offset = float(argv.pop(0))
                except Exception as e: print(e)
            case '-g' | '--granularity':
                try: parameters.granularity = int(argv.pop(0))
                except Exception as e: print(e)
            case '-m' | '--mode':
                try: 
                    match argv.pop(0).lower().strip()[:3]:
                        case 'get' | '0': 
                            parameters.mode = mode_t.get_distribution
                        case 'gen' | '1':
                            parameters.mode = mode_t.generate
                        case s:
                            raise ValueError(f'Invalid mode {s}')
                except Exception as e: print(e)
            case '-f' | '--f':
                try: parameters.f = argv.pop(0)
                except Exception as e: print(e)
            case '-h' | '--help':
                print_help = True
            case s:
                print(f'Invalid option: {s}')
                print_help = True
    if print_help: 
        print(help_str)
        
    console_log('Parameters:')
    for k, v in parameters.__dict__.items():
        console_log(f'    {k}: {v}')
    init()
    if parameters.mode == mode_t.get_distribution:
        gen_distribution()
    elif parameters.mode == mode_t.generate:
        with open(parameters.f, 'rb') as fp:
            dump : Optional[dump_t] = pickle.load(fp)
            global plan
            plan = dump.plan
            parameters = dump.parameters
            generate([lambda: console_log(f'executing {i}') for i in range(parameters.n)])
            
if __name__ == "__main__":
    main()
