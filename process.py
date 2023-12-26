from math import ceil

class process(object):
    def __init__(self, id, exp_dist_lambda):
        self.exp_dist_lambda = exp_dist_lambda
        self.num_cpu_bursts = 0
        self.arrival_time = 0
        self.cpu_burst_time = []
        self.io_burst_time = []
        self.id = id
        self.state = "BLOCK"
        self.arrived = False
        self.tau = ceil(1 / exp_dist_lambda)
        self.time_left = 0
        self.last_burst_time = 0
        self.enter_time = 0
        self.time_spent = 0
        self.name = str(self)
        self.terminate_time = 0
        self.sum_cpu_burst_time = 0
        self.sum_io_burst_time = 0
    
    def set_num_cpu_bursts(self, t):
        self.num_cpu_bursts = t
    
    def set_arrival_time(self, t):
        self.arrival_time = t

    def set_cpu_burst_time(self, t):
        self.cpu_burst_time = t

    def set_io_burst_time(self, t):
        self.io_burst_time = t
    
    def __str__(self):
        dict_name = {
            0: "A", 1: "B", 2: "C", 3: "D", 4: "E",
            5: "F", 6: "G", 7: "H", 8: "I", 9: "J", 10: "K", 11: "L", 12: "M", 13: "N", 14: "O", 15: "P",
            16: "Q", 17: "R", 18: "S", 19: "T", 20: "U", 21: "V", 22: "W", 23: "X", 24: "Y", 25: "Z"
        }
        return dict_name[self.id]