# Bursty workload generator
## Parameters (main.py):
  - **\(a_1\)**: (outer/low-pass) skewness, aka. how even are workload spread across groups, lower more skewed \(a_1\to1\): most skewed, \(a_1\to+\infin\): uniform
  - **\(a_2\)**: (inner/high-pass) skewness, aka. how skewed data is within each group
  - **n**: number of samples
  - **granularity**: number of groups (big spikes if a1 is low)
  - **duration**: range of samples (in seconds)
  - **offset**: offset of samples (delay in seconds)
  - **f**: save/load file location (default: ./plan.bin)
  - **mode**: 
      - get_distribution: get and save the distribution (default)
      - generate: test workload generation with dummy workload

## Visualize result (vis_plan.py):
**Uniform high freq, skewed low freq**: `python .\main.py -a1 22 -a2 2.2 -n 10000 -d 50000 -g 100 && python .\vis_plan.py`
![Figure_1](/assets/Figure_1.png)
**Skewed high freq, uniform low freq**: `python .\main.py -a1 1.22 -a2 22 -n 10000 -d 50000 -g 100 && python .\vis_plan.py`
![Figure_5](/assets/Figure_4.png)
**Skewed both freq**: `python .\main.py -a1 1.5 -a2 1.1 -n 10000 -d 50000 -g 100 && python .\vis_plan.py`
![Figure_2](/assets/Figure_2.png)
**Skewed both freq, less groups**: `python .\main.py -a1 1.5 -a2 1.5 -n 10000 -d 50000 -g 10 && python .\vis_plan.py`
![Figure_3](/assets/Figure_3.png)
**Uniform both freq**: `python .\main.py -a1 22 -a2 22 -n 10000 -d 50000 -g 10 && python .\vis_plan.py`
![Figure_4](/assets/Figure_0.png)