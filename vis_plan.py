from common import *
import matplotlib.pyplot as plt

plan : Optional[dump_t] = None
with open('plan.bin', 'rb') as fp:
    plan : dump_t = pickle.load(fp)

plt.xlabel('Time point (s)')
plt.ylabel('Number of queries issued')
plt.hist(plan.plan, bins = 1000, density = False)
plt.show()
