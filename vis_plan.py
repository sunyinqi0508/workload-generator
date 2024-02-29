from common import *
import matplotlib.pyplot as plt
import seaborn as sns
import os, sys, subprocess, threading

plan : Optional[dump_t] = None
vis_parameters = {
    'bins': 1000, 
    'vis': 0,  
    'bw': 5.
}

def load_plan():
    global plan
    with open('plan.bin', 'rb') as fp:
        plan = pickle.load(fp)
        
def close_figure_on_escape(event):
    if event.key == 'escape':
        plt.close(event.canvas.figure)
            
def vonmises_kde(data, kappa, n_bins=100):
    from scipy.special import i0
    bins = np.linspace(-np.pi, np.pi, n_bins)
    x = np.linspace(-np.pi, np.pi, n_bins)
    # integrate vonmises kernels
    kde = np.exp(kappa*np.cos(x[:, None]-data[None, :])).sum(1)/(2*np.pi*i0(kappa))
    kde /= np.trapz(kde, x=bins)
    return bins, kde
def show_plan(block = True):
    global plan
    plt.figure().canvas.mpl_connect('key_press_event', close_figure_on_escape)
    plt.xlabel('Time point (s)')
    plt.ylabel('Number of queries issued')
    plt.autoscale(enable=True, axis='x', tight=False)
    plt.yscale('linear')
    if switches['log']:
        plt.yscale('symlog')
    histtype = 'bar'
    n_bins = vis_parameters['bins']
    if vis_parameters['vis'] == 2:
        from KDEpy import FFTKDE
        bw = vis_parameters['bw']
        data = np.array(plan.plan)
        lower_bound = np.min(data) # plan.parameters.offset
        upper_bound = np.max(data) # plan.parameters.duration + plan.parameters.offset
        data = np.concatenate((data, lower_bound - data, 2*upper_bound - data))
        kde = FFTKDE(bw=bw, kernel='gaussian').fit(data)
        x, y = kde.evaluate()
        xy = [(xx, yy) for xx, yy in zip(x, y) if lower_bound <= xx <= upper_bound]
        x, y = zip(*xy)
        y = np.array(y)
        y *= (plan.parameters.n / np.sum(y))
        plt.plot(x, y)
    else:
        if vis_parameters['vis'] == 0:
            counts, _ = np.histogram(plan.plan, bins = n_bins, density=False)
            counts = np.array([cc for c in counts for cc in np.full(n_bins, c/n_bins)])
            # bins = bins[:-1] + np.diff(bins)/2
            from scipy.signal import savgol_filter
            from scipy.ndimage import gaussian_filter1d
            counts = savgol_filter(counts, window_length=10, polyorder=4)
            counts = np.convolve(counts, 5, mode = 'full')
            counts = gaussian_filter1d(counts, 3)
            bins = np.linspace(0, plan.parameters.n, len(counts))
            plt.plot(bins, counts)
        else:
            plt.hist(plan.plan, 
                    bins = vis_parameters['bins'], 
                    histtype=histtype, 
                    density = False
            )
    plt.show(block=block)
mutex = threading.Lock()
show_plan_flag = 4

def ui_thread():
    global show_plan_flag
    plt.ion()
    plt.rcParams['keymap.quit'].append('escape')  
    while(True):
        try: plt.pause(0.1)
        except: ...
        from time import sleep
        sleep(0.1)
        if show_plan_flag < 3:
            mutex.acquire()
            try:
                match show_plan_flag:
                    case 0:
                        show_plan(False)
                    case 1:
                        plt.close()
                    case 2:
                        save_plan()
                    case _:
                        print(f'Invalid flag {show_plan_flag}')
            except Exception as e:
                print(e)
            show_plan_flag = 4
            mutex.release()

def save_plan(filename = None):
    if not filename:
        filename = (
                f'o{distribution_name[plan.parameters.outer]}'
                f'_i{distribution_name[plan.parameters.inner]}'
                f'_n{plan.parameters.n}'
                f'_d{plan.parameters.duration}'
                f'_g{plan.parameters.granularity}'
                f'_a1{plan.parameters.a1}'
                f'_b1{plan.parameters.b1}'
                f'_a2{plan.parameters.a2}'
                f'_b2{plan.parameters.b2}'
                f'_s{plan.parameters.shfl}'
                '.png')
    try:
        plt.savefig(filename)
    except Exception as e:
        print(e)
        
def restart():
    subprocess.Popen(
        [
            sys.executable, 
            *sys.argv
        ], 
        shell = True,         
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
    )
    os.abort()

def vis_threaded(op = 0):
    global show_plan_flag
    mutex.acquire()
    show_plan_flag = op
    mutex.release()

commands = {
    'load': load_plan,
    'show': lambda: vis_threaded(0),
    'save': lambda: vis_threaded(2), 
    'close': lambda: vis_threaded(1), 
    'restart': restart,
    'exit': lambda: os.abort(),
}

flags = {
    'on': True,
    'off': False
}

switches = {
    'show': False, 
    'save': False,
    'log': False
}

if ('TERM_PROGRAM' in os.environ.keys() or 
    any('-i' in v for v in sys.argv[1:])): # Interactive mode
    print('Interactive mode')
    def exec_cmd(cmd):
        global show_plan_flag
        try:
            subprocess.run(
                [sys.executable, 
                 './main.py', 
                 *cmd.split(' ')
            ])
            load_plan()
            if switches['show']:
                vis_threaded(0)
                # show_plan(False)
            if switches['save']:
                vis_threaded(2)
        except Exception as e:
            print(e)
    def prompt_thread():
        while(True):
            cmd = input('Enter command: ')
            s_cmd = cmd.lower().strip() 
            if s_cmd in commands:
                try: commands[cmd]() 
                except Exception as e: print(e)
            elif ' ' in s_cmd:
                splits_cmd = s_cmd.split(' ')
                if splits_cmd[0] in switches and splits_cmd[1] in flags:
                    switches[splits_cmd[0]] = flags[splits_cmd[1]]
                elif splits_cmd[0] in vis_parameters:
                    ty = type(vis_parameters[splits_cmd[0]])
                    vis_parameters[splits_cmd[0]] = ty(splits_cmd[1])
                else:
                    exec_cmd(cmd)
            else:
                exec_cmd(cmd)
    threading.Thread(target=prompt_thread).start()
    ui_thread()
else:
    load_plan()
    show_plan()
    save_plan()        

