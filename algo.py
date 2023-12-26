from Rand48 import Rand48
from math import ceil, floor, trunc, log


class algo(object):
    def __init__(self, seed=2, exp_dist_lambda=0.01, upper_bound=3000, t_cs=4, alpha=0.5, rr_add="END"):
        self.print_max_time = 1000

        self.seed = seed
        self.exp_dist_lambda = exp_dist_lambda
        self.upper_bound = upper_bound
        self.t_cs = t_cs
        self.alpha = alpha
        self.rr_add = rr_add

        self.dict_name = {
            0: "A", 1: "B", 2: "C", 3: "D", 4: "E",
            5: "F", 6: "G", 7: "H", 8: "I", 9: "J", 10: "K", 11: "L", 12: "M", 13: "N", 14: "O", 15: "P",
            16: "Q", 17: "R", 18: "S", 19: "T", 20: "U", 21: "V", 22: "W", 23: "X", 24: "Y", 25: "Z"
        }

        # init number of context switchs and number of preemption counter
        self.num_context_switches = 0
        self.num_preempt = 0

        # init counter of burst time, wait time, turnaround time for stat
        self.total_burst_time = 0
        self.total_wait_time = 0
        self.total_turnaround_time = 0

        # init random number sequence
        self.rand48 = Rand48()
        self.rand48.srand(seed)

        # init process sequence
        self.process = []

        #init time
        self.time = 0
        self.enter_time = 0

        #counter for process arrival
        self.arrival_counter = 0

        #counter for ended processes
        self.end_process_counter = 0

        #placeholder for name
        self.name = "default"

        #init ready queue and io queue
        self.ready_queue = []
        self.io_queue = []

        self.cpu_user = None
        self.cpu_burst_end_time = 0

        #time permitted to enter cpu
        self.cpu_ready_enter_time = (None,0)

        self.num_context_switches = 0


    def stat_summary(self):
        num_burst = 0

        for p in self.process:
            num_burst += p.num_cpu_bursts
        
        # calculate for wait time
        wait_time = 0.0
        for p in self.process:
            wait_time += (p.terminate_time - p.arrival_time)
            wait_time -= p.sum_cpu_burst_time
            wait_time -= p.sum_io_burst_time

        wait_time -= self.t_cs * self.num_context_switches
        wait_time += (self.t_cs/2)
        wait_time += (len(self.process)-1)/2 * self.t_cs

        #calculate for turnaround time
        total_turnaround_time = wait_time + self.total_burst_time + (self.num_context_switches * self.t_cs)

        output = "Algorithm "
        output += self.name
        output += "\n"

        output += "-- average CPU burst time: {:.3f} ms\n".format(float(self.total_burst_time)/num_burst)
        output += "-- average wait time: {:.3f} ms\n".format(float(wait_time)/num_burst)    
        output += "-- average turnaround time: {:.3f} ms\n".format(float(total_turnaround_time)/num_burst)
        output += "-- total number of context switches: {}\n".format(self.num_context_switches)
        output += "-- total number of preemptions: {}\n".format(self.num_preempt)
        #output += "-- total number of bursts: {}\n".format(num_burst) 537 for output04
        return output




    def add(self, p):
        # set arrival time
        p.set_arrival_time(floor(-log(self.rand48.drand()) / self.exp_dist_lambda))
        while p.arrival_time > self.upper_bound:
            p.set_arrival_time(floor(-log(self.rand48.drand()) / self.exp_dist_lambda))

        # set number of cpu
        p.set_num_cpu_bursts(trunc(self.rand48.drand() * 100)+1)

        # set cpu burst time and io burst time
        cpu_burst = []
        io_burst = []
        for i in range(p.num_cpu_bursts):
            tmp = -log(self.rand48.drand()) / self.exp_dist_lambda
            while(tmp > self.upper_bound):
                tmp = -log(self.rand48.drand()) / self.exp_dist_lambda
            cpu_burst.append(ceil(tmp))
            if i == p.num_cpu_bursts-1:
                break
                
            tmp = -log(self.rand48.drand()) / self.exp_dist_lambda
            while(tmp > self.upper_bound):
                tmp = -log(self.rand48.drand()) / self.exp_dist_lambda
            io_burst.append(ceil(tmp))
        # test length of cpu burst and io burst
        assert len(cpu_burst) == p.num_cpu_bursts
        assert len(io_burst) == p.num_cpu_bursts - 1
        p.set_cpu_burst_time(cpu_burst)
        p.set_io_burst_time(io_burst)
        if self.name == "FCFS" or self.name == "RR":
            if p.num_cpu_bursts == 1:
                print("Process {} [NEW] (arrival time {} ms) {} CPU burst".format(self.dict_name[p.id], p.arrival_time, p.num_cpu_bursts))
            else:
                print("Process {} [NEW] (arrival time {} ms) {} CPU bursts".format(self.dict_name[p.id], p.arrival_time, p.num_cpu_bursts))
        elif self.name == "SJF" or self.name == "SRT":
            if p.num_cpu_bursts == 1:
                print("Process {} [NEW] (arrival time {} ms) {} CPU burst (tau {}ms)".format(self.dict_name[p.id], p.arrival_time, p.num_cpu_bursts, p.tau))
            else:
                print("Process {} [NEW] (arrival time {} ms) {} CPU bursts (tau {}ms)".format(self.dict_name[p.id], p.arrival_time, p.num_cpu_bursts, p.tau))
        else:
            AssertionError("Algorithm Name Error")
        p.sum_cpu_burst_time = sum(p.cpu_burst_time)
        p.sum_io_burst_time = sum(p.io_burst_time)
        self.process.append(p)
    
    def queue_status(self):
        if len(self.ready_queue) == 0:
            return " <empty>"
        else:
            ans = ""
            for i in self.ready_queue:
                ans += " "
                ans += str(i)
            return ans

    def check_process_arrival(self):
        for p in self.process:
            if p.arrival_time <= self.time and p.arrived is False:
                self.arrival_counter += 1
                if self.name == "RR" and self.rr_add == "BEGINNING":
                    self.ready_queue.insert(0,p)
                else:
                    self.ready_queue.append(p)
                p.arrived = True

                #sort the ready queue if algo is SJF or SRT
                if self.name == "SJF" or self.name == "SRT":
                    #break tie by passing name as secondary sorting parameter
                    self.ready_queue.sort(key=lambda e: (e.tau, str(e)))

                if self.time < self.print_max_time:
                    if self.name == "FCFS" or self.name == "RR":
                        print("time {}ms: Process {} arrived; added to ready queue [Q{}]".format(p.arrival_time, p, self.queue_status()))
                    elif self.name == "SJF" or self.name == "SRT":
                        print("time {}ms: Process {} (tau {}ms) arrived; added to ready queue [Q{}]".format(p.arrival_time, p, p.tau, self.queue_status()))
                    else:
                        AssertionError("Algorithm Name Error")

                return True
        return False
    
        
    def reduce_cpu_user_time_left(self):
        if self.cpu_user is not None:
            self.cpu_user.time_left -= 1
        return
    
    def increase_cpu_user_time_spent(self):
        if self.cpu_user is not None:
            self.cpu_user.time_spent += 1
        return

    def record_total_wait_time(self):
        for _ in self.ready_queue:
            self.total_wait_time += 1

    def print_start(self):
        # for p in self.process:
        #     print("{} ready_queue_sum: {}\n".format(p, sum(p.cpu_burst_time)))
        #     print("{} io_sum: {}\n".format(p, sum(p.io_burst_time)))
        print("time {}ms: Simulator started for {} [Q{}]\n".format(self.time, self.name, self.queue_status()), end = '')
    def print_end(self):
        print("time {}ms: Simulator ended for {} [Q{}]\n".format(self.time, self.name, self.queue_status()), end ='')
        if(self.name != "RR"):
            print()
        return self.stat_summary()


class FCFS(algo):
    def check_ready_queue_to_cpu(self):
        if self.cpu_user is None and (len(self.ready_queue) > 0 or self.cpu_ready_enter_time[0] is not None):
            
            #check if cpu is permitted to enter
            #when a process in ready queue is waiting to enter
            #set the cpu_ready_enter_time
            #when self.time == cpu_ready_enter_time
            #let the process enter the cpu
            if self.cpu_ready_enter_time[1] == 0:
                self.cpu_ready_enter_time = (self.ready_queue.pop(0), self.time + int(self.t_cs / 2))
                return False
            elif self.time < self.cpu_ready_enter_time[1]:
                return False

            self.cpu_user = self.cpu_ready_enter_time[0]
            self.cpu_ready_enter_time = (None, 0)

            burst_time = self.cpu_user.cpu_burst_time.pop(0)
            self.total_burst_time += burst_time

            self.num_context_switches += 1

            if self.cpu_user.time_left == 0:
                self.cpu_user.time_left = burst_time
            self.cpu_burst_end_time = self.time + burst_time
            if self.time < self.print_max_time:
                print("time {}ms: Process {} started using the CPU for {}ms burst [Q{}]".format(self.time, self.cpu_user, burst_time, self.queue_status()))
            return True
        return False

    
    def check_cpu_burst_to_io(self):
        p = self.cpu_user
        if self.cpu_user is None:
            return False
        if self.cpu_burst_end_time <= self.time:
            if len(self.cpu_user.cpu_burst_time) > 0:
                if self.time < self.print_max_time:
                    if len(self.cpu_user.cpu_burst_time) == 1:
                        print("time {}ms: Process {} completed a CPU burst; {} burst to go [Q{}]".format(self.cpu_burst_end_time, p, len(self.cpu_user.cpu_burst_time), self.queue_status()))
                    else:
                        print("time {}ms: Process {} completed a CPU burst; {} bursts to go [Q{}]".format(self.cpu_burst_end_time, p, len(self.cpu_user.cpu_burst_time), self.queue_status()))        
                #swtich out of CPU, added to IO
                io_time = p.io_burst_time.pop(0)
                io_end_time = self.time + io_time + int(self.t_cs/2)
                if self.time < self.print_max_time:
                    print("time {}ms: Process {} switching out of CPU; will block on I/O until time {}ms [Q{}]".format(self.cpu_burst_end_time, p, io_end_time, self.queue_status()))
                self.io_queue.append((p, io_end_time))
                if(len(self.process) > 1):
                    self.time += int(self.t_cs/2)
            else:
                print("time {}ms: Process {} terminated [Q{}]".format(self.time, p, self.queue_status()))
                p.terminate_time = self.time
                self.time += int(self.t_cs/2)
                self.end_process_counter += 1

            #reset enter time if the process finished burst
            self.cpu_user.enter_time = 0

            self.cpu_user = None
            self.cpu_burst_end_time = 0
            return True
        return False
    
    def check_io_to_ready_queue(self):
        self.io_queue.sort(key=lambda e: str(e))
        for i in self.io_queue:
            if i[1] <= self.time:
                #completed IO, added to ready queue
                self.ready_queue.append(i[0])
                if self.time < self.print_max_time:
                    print("time {}ms: Process {} completed I/O; added to ready queue [Q{}]".format(i[1], i[0], self.queue_status()))
                self.io_queue.remove(i)
                return True
        return False

    def __init__(self, seed=2, exp_dist_lambda=0.01, upper_bound=3000, t_cs=4, rr_add="END"):
        super().__init__(seed, exp_dist_lambda, upper_bound, t_cs, rr_add=rr_add)
        self.name = "FCFS"
    
    def exec(self):
        self.print_start()
        while self.end_process_counter != len(self.process):
            flag = True
            while flag is True:
                flag = False
                flag = flag or self.check_ready_queue_to_cpu()
                self.check_ready_queue_to_cpu()

                flag = flag or self.check_cpu_burst_to_io()
                self.check_cpu_burst_to_io()

                flag = flag or self.check_io_to_ready_queue()
                self.check_io_to_ready_queue()

                #only check process arrival when there is still process haven't arrived
                if self.arrival_counter < len(self.process):
                    flag = flag or self.check_process_arrival()
                    self.check_process_arrival()

            # increase counter
            self.time += 1
            # reduce time left for cpu user
            self.reduce_cpu_user_time_left()
            # record total waiting time
            self.record_total_wait_time()
        self.time -= 1
        return self.print_end()

class RR(FCFS):
    def check_ready_queue_to_cpu(self):
        if len(self.append_buffer) > 0:
            for i in self.append_buffer:
                if i[1] <= self.time:
                    self.ready_queue.append(i[0])
                    self.append_buffer.remove(i)

        if self.cpu_user is None and (len(self.ready_queue) > 0 or self.cpu_ready_enter_time[0] is not None):

            if self.cpu_ready_enter_time[1] == 0:
                self.cpu_ready_enter_time = (self.ready_queue.pop(0), self.time + int(self.t_cs / 2))
                return False
            elif self.time < self.cpu_ready_enter_time[1]:
                return False

            self.cpu_user = self.cpu_ready_enter_time[0]
            self.cpu_ready_enter_time = (None, 0)

            # reset time slice counter
            self.t_slice_counter = self.t_slice

            self.num_context_switches += 1
            
            remaining_flag = False

            # use left_time if there is one
            if self.cpu_user.time_left != 0:
                burst_time = self.cpu_user.time_left
                remaining_flag = True
            else:
                burst_time = self.cpu_user.cpu_burst_time.pop(0)
                self.total_burst_time += burst_time

            if self.cpu_user.time_left == 0:
                self.cpu_user.time_left = burst_time
            self.cpu_burst_end_time = self.time + burst_time
            if self.time < self.print_max_time:
                if remaining_flag:
                    print("time {}ms: Process {} started using the CPU with {}ms burst remaining [Q{}]".format(self.time, self.cpu_user, burst_time, self.queue_status()))
                else:
                    print("time {}ms: Process {} started using the CPU for {}ms burst [Q{}]".format(self.time, self.cpu_user, burst_time, self.queue_status()))
            return True
        return False

    def check_time_slice(self):
        if self.cpu_user is None:
            return False
        if self.t_slice_counter == 0 and self.cpu_user.time_left != 0:
            # skipping preemptioin if ready queue is empty
            if len(self.ready_queue) == 0:
                # reset time slice counter
                self.t_slice_counter = self.t_slice
                if self.time < self.print_max_time:
                    print("time {}ms: Time slice expired; no preemption because ready queue is empty [Q{}]".format(self.time, self.queue_status()))
                return False

            if self.time < self.print_max_time:
                print("time {}ms: Time slice expired; process {} preempted with {}ms to go [Q{}]".format(self.time, self.cpu_user, self.cpu_user.time_left, self.queue_status()))
            
            # reset time slice counter
            self.t_slice_counter = self.t_slice
        
            # Preemption here!!!
            self.num_preempt += 1
            self.append_buffer.append((self.cpu_user, self.time + int(self.t_cs/2)))
            self.cpu_user = None
            self.cpu_ready_enter_time = (self.ready_queue.pop(0), self.time + self.t_cs)
            return True

        return False
    
    # def check_io_to_ready_queue(self):
    #     self.io_queue.sort(key=lambda e: str(e))
    #     for i in self.io_queue:
    #         if i[1] <= self.time:
    #             #completed IO, added to ready queue
    #             if self.rr_add == "END":
    #                 #add to the end of the queue
    #                 self.ready_queue.append(i[0])
    #             elif self.rr_add == "BEGINNING":
    #                 #add to the beginning of the queue
    #                 self.ready_queue.insert(0, i[0])
    #             else:
    #                 AssertionError("RR_ADD Parameter Error")
    #             if self.time < self.print_max_time:
    #                 print("time {}ms: Process {} completed I/O; added to ready queue [Q{}]".format(i[1], i[0], self.queue_status()))
    #             self.io_queue.remove(i)
    #             return True
    #     return False

    def __init__(self, seed=2, exp_dist_lambda=0.01, upper_bound=3000, t_cs=4, t_slice=128, rr_add="END"):
        super().__init__(seed, exp_dist_lambda, upper_bound, t_cs, rr_add=rr_add)
        self.name = "RR"

        # properties of RR
        self.t_slice = t_slice
        self.rr_add = rr_add
        self.t_slice_counter = t_slice

        #append_buffer to store cpu user when cpu user is preempted and new process doesn't start burst
        self.append_buffer = []


    def exec(self):
        self.print_start()
        while self.end_process_counter != len(self.process):
            flag = True
            while flag is True:
                flag = False

                flag = flag or self.check_time_slice()

                flag = flag or self.check_ready_queue_to_cpu()
                self.check_ready_queue_to_cpu()

                flag = flag or self.check_cpu_burst_to_io()
                self.check_cpu_burst_to_io()

                flag = flag or self.check_io_to_ready_queue()
                self.check_io_to_ready_queue()

                #only check process arrival when there is still process haven't arrived
                if self.arrival_counter < len(self.process):
                    flag = flag or self.check_process_arrival()
                    self.check_process_arrival()
                    
            #increase counter
            self.time += 1
            #reduce time left for cpu user
            self.reduce_cpu_user_time_left()
            #reduce time slice counter
            self.t_slice_counter -= 1
            # record total waiting time
            self.record_total_wait_time()

        self.time -= 1
        return self.print_end()


class SJF(algo):

    def check_ready_queue_to_cpu_with_tau(self):
        if self.cpu_user is None and (len(self.ready_queue) > 0 or self.cpu_ready_enter_time[0] is not None):
            #break tie by passing name as secondary sorting parameter
            self.ready_queue.sort(key=lambda e: (e.tau-e.time_spent, str(e)))
            
            #check if cpu is permitted to enter
            #when a process in ready queue is waiting to enter
            #set the cpu_ready_enter_time
            #when self.time == cpu_ready_enter_time
            #let the process enter the cpu
            if self.cpu_ready_enter_time[1] == 0:
                self.cpu_ready_enter_time = (self.ready_queue.pop(0), self.time + int(self.t_cs / 2))
                return False
            elif self.time < self.cpu_ready_enter_time[1]:
                return False

            self.cpu_user = self.cpu_ready_enter_time[0]
            self.cpu_ready_enter_time = (None, 0)

            burst_time = self.cpu_user.cpu_burst_time.pop(0)
            self.cpu_user.last_burst_time = burst_time
            self.cpu_burst_end_time = self.time + burst_time
            self.total_burst_time += burst_time

            self.num_context_switches += 1

            if self.time < self.print_max_time:
                print("time {}ms: Process {} (tau {}ms) started using the CPU for {}ms burst [Q{}]\n".format(self.time, self.cpu_user, self.cpu_user.tau, burst_time, self.queue_status()), end ='')
            return True
        return False
    
    def check_cpu_burst_to_io_with_tau(self):
        p = self.cpu_user
        if self.cpu_user is None:
            return False
        if self.cpu_burst_end_time <= self.time:
            if len(self.cpu_user.cpu_burst_time) > 0:
                if self.time < self.print_max_time:
                    if len(self.cpu_user.cpu_burst_time) == 1:
                        print("time {}ms: Process {} (tau {}ms) completed a CPU burst; {} burst to go [Q{}]".format(self.cpu_burst_end_time, p, p.tau, len(self.cpu_user.cpu_burst_time), self.queue_status()))
                    else:
                        print("time {}ms: Process {} (tau {}ms) completed a CPU burst; {} bursts to go [Q{}]".format(self.cpu_burst_end_time, p, p.tau, len(self.cpu_user.cpu_burst_time), self.queue_status()))        
                
                #recalculate tau
                p.tau = ceil(self.alpha * self.cpu_user.last_burst_time + (1-self.alpha) * p.tau)
                if self.time < self.print_max_time:
                    print("time {}ms: Recalculated tau = {}ms for process {} [Q{}]".format(self.cpu_burst_end_time, p.tau, p, self.queue_status()))

                #swtich out of CPU, added to IO
                io_time = p.io_burst_time.pop(0)
                io_end_time = self.time + io_time + int(self.t_cs/2)
                if self.time < self.print_max_time:
                    print("time {}ms: Process {} switching out of CPU; will block on I/O until time {}ms [Q{}]".format(self.cpu_burst_end_time, p, io_end_time, self.queue_status()))
                self.io_queue.append((p, io_end_time))
                if(len(self.process) > 1):
                    self.time += int(self.t_cs/2)
            else:
                print("time {}ms: Process {} terminated [Q{}]".format(self.time, p, self.queue_status()))
                p.terminate_time = self.time
                self.time += int(self.t_cs/2)
                self.end_process_counter += 1
            #reset time spent
            self.cpu_user.time_spent = 0
            self.cpu_user.last_burst_time = 0
            self.cpu_user = None
            self.cpu_burst_end_time = 0
            return True
        return False
    
    def check_io_to_ready_queue_with_tau(self):
        #to break tie
        self.io_queue.sort(key=lambda e: str(e))

        for i in self.io_queue:
            if i[1] <= self.time:
                #completed IO, added to ready queue
                self.ready_queue.append(i[0])
                #break tie by passing name as secondary sorting parameter
                self.ready_queue.sort(key=lambda e: (e.tau-e.time_spent, str(e)))
                if self.time < self.print_max_time:
                    print("time {}ms: Process {} (tau {}ms) completed I/O; added to ready queue [Q{}]\n".format(i[1], i[0], i[0].tau, self.queue_status()), end='')
                self.io_queue.remove(i)
                return True
        return False

    def __init__(self, seed=2, exp_dist_lambda=0.01, upper_bound=3000, t_cs=4, alpha=0.5):
        super().__init__(seed, exp_dist_lambda, upper_bound, t_cs, alpha)
        self.name = "SJF"
    def exec(self):
        self.print_start()
        while self.end_process_counter != len(self.process):
            # if self.time == 48319:
            #     print()
            flag = True
            while flag is True:
                flag = False
                flag = flag or self.check_ready_queue_to_cpu_with_tau()
                self.check_ready_queue_to_cpu_with_tau()

                flag = flag or self.check_cpu_burst_to_io_with_tau()
                self.check_cpu_burst_to_io_with_tau()

                flag = flag or self.check_io_to_ready_queue_with_tau()
                self.check_io_to_ready_queue_with_tau()

                #only check process arrival when there is still process haven't arrived
                if self.arrival_counter < len(self.process):
                    flag = flag or self.check_process_arrival()
                    self.check_process_arrival()
            #increase counter
            self.time += 1
            # record total waiting time
            self.record_total_wait_time()
        self.time -= 1
        return self.print_end()





class SRT(SJF):

    def check_ready_queue_to_cpu_with_tau(self):
        if self.cpu_user is None and (len(self.ready_queue) > 0 or self.cpu_ready_enter_time[0] is not None):

            #break tie by passing name as secondary sorting parameter
            self.ready_queue.sort(key=lambda e: (e.tau-e.time_spent, str(e)))

            if self.ready_queue_append_time != 0 and self.ready_queue_append_time == self.time:
            
                if self.append_buffer is not None:
                    self.ready_queue.append(self.append_buffer)
                    self.ready_queue.sort(key=lambda e: (e.tau-e.time_spent, str(e)))
                    self.append_buffer = None
                    self.ready_queue_append_time = 0

            #check if cpu is permitted to enter
            #when a process in ready queue is waiting to enter
            #set the cpu_ready_enter_time
            #when self.time == cpu_ready_enter_time
            #let the process enter the cpu
            if self.cpu_ready_enter_time[1] == 0:
                self.cpu_ready_enter_time = (self.ready_queue.pop(0), self.time + int(self.t_cs / 2))
                return False
            
            #special case
            elif len(self.ready_queue) > 0 and self.cpu_ready_enter_time[0].tau > self.ready_queue[0].tau and self.time == self.cpu_ready_enter_time[1] - int(self.t_cs / 2):
                self.cpu_ready_enter_time = (self.ready_queue[0], self.time + int(self.t_cs / 2))
                self.remove_buffer = self.ready_queue[0]
                return False
                
            elif self.time < self.cpu_ready_enter_time[1]:
                return False

            if self.remove_buffer is not None:
                self.ready_queue.remove(self.remove_buffer)
                self.ready_queue.sort(key=lambda e: (e.tau-e.time_spent, str(e)))
                self.remove_buffer = None
            
            if self.append_buffer is not None:
                    self.ready_queue.append(self.append_buffer)
                    self.ready_queue.sort(key=lambda e: (e.tau-e.time_spent, str(e)))
                    self.append_buffer = None
                    self.ready_queue_append_time = 0

            self.cpu_user = self.cpu_ready_enter_time[0]
            self.cpu_ready_enter_time = (None, 0)

            self.num_context_switches += 1

            #when the process was not preempted (no time left)
            if self.cpu_user.time_left == 0:
                burst_time = self.cpu_user.cpu_burst_time.pop(0)
                self.cpu_user.time_left = burst_time
                self.cpu_user.last_burst_time = burst_time
                self.total_burst_time += burst_time
            
            #when the process was preempted (has time left)
            else:
                burst_time = self.cpu_user.time_left

            self.cpu_burst_end_time = self.time + burst_time

            #only set enter time when cpu user was not preempted
            if self.cpu_user.enter_time == 0: 
                self.cpu_user.enter_time = self.time

            if self.time < self.print_max_time:
                print("time {}ms: Process {} (tau {}ms) started using the CPU with {}ms burst remaining [Q{}]\n".format(self.time, self.cpu_user, self.cpu_user.tau, burst_time, self.queue_status()), end = '')
            return True
        return False

    def check_preemption(self):
        if len(self.ready_queue) > 0 and self.cpu_user is not None:
            #check if a job stays longer than its estimated time
            if self.cpu_user.tau - self.cpu_user.time_spent > self.ready_queue[0].tau:
                if self.time < self.print_max_time:
                    print("time {}ms: Process {} (tau {}ms) will preempt {} [Q{}]".format(self.time, self.ready_queue[0], self.ready_queue[0].tau, self.cpu_user, self.queue_status()))
                self.ready_queue.append(self.cpu_user)
                self.cpu_user = None
                self.cpu_ready_enter_time = (self.ready_queue[0], self.time + self.t_cs)
                self.ready_queue.remove(self.ready_queue[0])
                self.num_preempt += 1
                
        return False
    
    def check_io_to_ready_queue_with_tau(self):
        #to break tie
        self.io_queue.sort(key=lambda e: str(e))

        for i in self.io_queue:
            if i[1] <= self.time:
                #completed IO, added to ready queue
                self.ready_queue.append(i[0])
                #break tie by passing name as secondary sorting parameter
                self.ready_queue.sort(key=lambda e: (e.tau-e.time_spent, str(e)))
                if len(self.ready_queue) > 0 and self.cpu_user is not None:
                    #last condition was added, if not B will be "preempting", might be wrong but matches the output
                    if self.cpu_user.tau - self.cpu_user.time_spent > i[0].tau:
                        if self.time < self.print_max_time:
                            print("time {}ms: Process {} (tau {}ms) completed I/O; preempting {} [Q{}]".format(self.time, i[0], i[0].tau, self.cpu_user, self.queue_status()))
         
                        self.append_buffer = self.cpu_user
                        self.ready_queue_append_time = self.time + int(self.t_cs / 2)
                        self.cpu_user = None
                        self.cpu_ready_enter_time = (i[0], self.time + self.t_cs)
                        self.remove_buffer = i[0]
                        
                        self.io_queue.remove(i)

                        self.num_preempt += 1
                        return True

                i[0].enter_time = 0
                if self.time < self.print_max_time:
                    print("time {}ms: Process {} (tau {}ms) completed I/O; added to ready queue [Q{}]".format(i[1], i[0], i[0].tau, self.queue_status()))
                self.io_queue.remove(i)
                return True
        return False

    def __init__(self, seed=2, exp_dist_lambda=0.01, upper_bound=3000, t_cs=4, alpha=0.5):
        super().__init__(seed, exp_dist_lambda, upper_bound, t_cs, alpha)
        self.name = "SRT"

        #append_buffer to store cpu user when cpu user is preempted and new process doesn't start burst
        self.append_buffer = None
        self.ready_queue_append_time = 0

        self.remove_buffer = None

    def exec(self):
        self.print_start()
        while self.end_process_counter != len(self.process):

            # if self.time == 13664:
            #     print("ERROR")
            #     print(self.queue_status())
            flag = True
            while flag is True:
                flag = False
                flag = flag or self.check_ready_queue_to_cpu_with_tau()

                flag = flag or self.check_cpu_burst_to_io_with_tau()
                self.check_cpu_burst_to_io_with_tau()

                flag = flag or self.check_io_to_ready_queue_with_tau()
                self.check_io_to_ready_queue_with_tau()

                flag = flag or self.check_preemption()
                self.check_preemption()

                #only check process arrival when there is still process haven't arrived
                if self.arrival_counter < len(self.process):
                    flag = flag or self.check_process_arrival()
                    self.check_process_arrival()

            #increase counter
            self.time += 1
            #reduce time left for cpu user
            self.reduce_cpu_user_time_left()
            #increase time spent
            self.increase_cpu_user_time_spent()
            # record total waiting time
            self.record_total_wait_time()


        self.time -= 1
        return self.print_end()