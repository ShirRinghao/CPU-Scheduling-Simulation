import sys
from algo import FCFS, SJF, SRT, RR
from process import process

if __name__ == "__main__":

    # load parameters
    n = int(sys.argv[1]) # number of processes to simulate
    seed = int(sys.argv[2]) # seed for srand48
    exp_dist_lambda = float(sys.argv[3]) # lambda for exponential distribution
    upper_bound = int(sys.argv[4]) # upper bound for rand48
    t_cs = int(sys.argv[5]) # t_cs: time to perform a context switch
    alpha = float(sys.argv[6]) # alpha for exponential averaging
    t_slice = int(sys.argv[7])
    
    rr_add = "END" # default value for rr_add   
    if len(sys.argv) == 9:
        rr_add = sys.argv[8]

    #init algorithms
    fcfs = FCFS(exp_dist_lambda=exp_dist_lambda, upper_bound=upper_bound, seed=seed, t_cs=t_cs)
    sjf = SJF(exp_dist_lambda=exp_dist_lambda, upper_bound=upper_bound, seed=seed, t_cs=t_cs, alpha=alpha)
    srt = SRT(exp_dist_lambda=exp_dist_lambda, upper_bound=upper_bound, seed=seed, t_cs=t_cs, alpha=alpha)
    rr = RR(exp_dist_lambda=exp_dist_lambda, upper_bound=upper_bound, seed=seed, t_cs=t_cs, t_slice=t_slice, rr_add=rr_add)

    f = open("simout.txt","w+")

    # Execute FCFS
    for i in range(n):
        p = process(i, exp_dist_lambda)
        fcfs.add(p)
    f.write(fcfs.exec())

    # Execute SJF
    for i in range(n):
        p = process(i, exp_dist_lambda)
        sjf.add(p)
    f.write(sjf.exec())

    # Execute SRT
    for i in range(n):
        p = process(i, exp_dist_lambda)
        srt.add(p)
    f.write(srt.exec())
    
    
    #Execute RR
    for i in range(n):
        p = process(i, exp_dist_lambda)
        rr.add(p)
    f.write(rr.exec())
