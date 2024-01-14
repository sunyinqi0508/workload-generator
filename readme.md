# Bursty workload generator
## How it works?
**Workload Generation `main.py -m get`**: This script will first split workloads into *g* bins using the *outer* distribution (default is zipf, can also be gaussian or uniform). Each bin will get $w_k$ workloads and $\Sigma_{k=0}^{g}w_k = n$. Each bin will start at $offset + \frac{duration}{g}*k$ second. The inner distribution will determine the time each workload query will be issued such that $\omega_{k, i} \sim \zeta(a_2, 1)$. $\omega_{k, i}$ is then scaled to the window of the k-th bin: $w_{k, i} = offset + (\omega_{k, i} + k)*s$, where $s = \frac{duration}{g}$. Consider using uniform distribution for less extreme distribution of works per bin.
**Visualization**: Use vis_plan.py to visualize the workload plan located in `./plan.bin` using a histogram.
**Executing workload `main.py -m exec`**: Issuing the workload using the plan in `./plan.bin`. The workloads being issued should be provided in a queue (list) of callables.

## Parameters (main.py):
  - **-g**: outer distribution (default zipf) can be gaussian (`-g gauss`) or uniform (`-g uniform`)
  - **$a_1$(--a1) or $\mu$(--mu)**: (outer/low-pass) skewness, aka. how even are workload spread across groups, lower more skewed \(a_1\to1\): most skewed, $a_1\to+\infin$: uniform. For gaussian distribution as outer distribution, this is the std ($\mu$).
  - **$a_2$(--a2) or --a**: (inner/high-pass) skewness, aka. how skewed data is within each group
  - **n**: number of samples
  - **granularity**: number of groups/bins (big spikes if a1 is low)
  - **duration**: range of samples (in seconds)
  - **offset**: offset of samples (delay in seconds)
  - **f**: save/load file location (default: ./plan.bin)
  - **mode**: 
      - get_distribution: get and save the distribution (default)
      - generate: test workload generation with dummy workload

## Visualize result (vis_plan.py):
**Uniform high freq, skewed low freq**: `python .\main.py -a1 22 -a2 2.2 -n 10000 -d 50000 -g 100 && python .\vis_plan.py`

![Figure_1](/assets/Figure_1.png)

**Skewed high freq, uniform low freq**: `python .\main.py -a1 1.75 -a2 22 -n 10000 -d 50000 -g 10 && python .\vis_plan.py`

![Figure_5](/assets/Figure_4.png)

**Skewed both freq**: `python .\main.py -a1 1.5 -a2 1.1 -n 10000 -d 50000 -g 100 && python .\vis_plan.py`

![Figure_2](/assets/Figure_2.png)

**Skewed both freq, less groups**: `python .\main.py -a1 1.5 -a2 1.5 -n 10000 -d 50000 -g 10 && python .\vis_plan.py`

![Figure_3](/assets/Figure_3.png)

**Uniform both freq**: `python .\main.py -a1 22 -a2 22 -n 10000 -d 50000 -g 10 && python .\vis_plan.py`

![Figure_4](/assets/Figure_0.png)