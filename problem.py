import random
from pprint import pprint
import enum
from typing import List, Tuple


class SchedulingMethod(enum.Enum):
    """Process scheduling method type
    """
    FCFS = 0  # First come, first served
    SJF = 1  # Shortest job first
    SRTF = 2  # Shortest remaining job first
    RR = 3  # Round robin


class Problem:
    """Process scheduling problem
    """

    def __init__(self, method: SchedulingMethod, times: List[Tuple[int, int]], quantum: int = None):
        """
        :param method: Process scheduling method
        :type method: SchedulingMethod

        :param times: List of (arrival time, execution time) pairs for each process
        :type times: List[Tuple[int, int]]

        :param quantum: Quantum for RR problem. Ignored if not RR problem.
        :type quantum: int
        """
        self.method = method
        self.times = times
        self.quantum = quantum

    @staticmethod
    def generate(method: SchedulingMethod, n_processes: int, max_time: int = 20, min_quantum: int = 2, max_quantum: int = 5):
        """Generate random problem
        """
        arrival_times = random.sample(range(1, max_time), n_processes)
        exec_times = [random.randint(1, t) for t in arrival_times]
        times = [(t1, t2) for t1, t2 in zip(arrival_times, exec_times)]

        method = random.choice(list(SchedulingMethod))

        # TODO: check if problem is uniquely solvable
        if method == SchedulingMethod.RR:
            quantum = random.randint(min_quantum, max_quantum)
            return Problem(method, times, quantum=quantum)
        else:
            return Problem(method, times)


class EventLogger:
    """Event logger
    """

    def __init__(self, n_processes: int):
        self.n_processes = n_processes
        self.events = []

    def begin_event(self, time: int):
        """Begin event at a point in time

        :param time: Time event occured
        :type time: int
        """
        self.curr_t = time
        self.curr_state = [None] * self.n_processes

    def end_event(self):
        """End and commit current event
        """
        self.events.append((self.curr_t, self.curr_state))

    def add(self, process: int, time_left: int):
        """Add processes to current event

        :param process: Index of process
        :type process: int

        :param time_left: Time left for process
        :type time_left: int
        """
        self.curr_state[process] = time_left

    def solve(self) -> List[Tuple[int, int]]:
        """Solve finish and wait times from event log

        :return: List of (finish time, wait time) pairs
        :rtype: List[Tuple[int, int]]
        """
        events = self.events
        n_processes = self.n_processes

        res = [None] * n_processes
        for p in range(n_processes):

            # Find finish time
            finish_t = 0
            for t, state in events:
                if state[p] == 0:
                    finish_t = t

            # Find wait time
            wait_t = 0
            start_idx = 0
            while events[start_idx][1][p] == None:
                start_idx += 1

            for i in range(start_idx, len(events)-1):
                t, state = events[i]
                next_t, next_state = events[i+1]

                # Exit if already done
                if state[p] == 0:
                    break

                # Not waiting if time left between events is not null and changes
                if state[p] != None and next_state[p] != None and state[p] != next_state[p]:
                    continue
                else:
                    wait_t += next_t - t
            res[p] = (finish_t, wait_t)

        return res


class Solver:
    """Process scheduling solver
    """

    def __init__(self, problem: Problem):
        self.problem = problem
        self.n_processes = len(problem.times)
        self.logger = EventLogger(self.n_processes)
        self.time_left = [exec_t for _, exec_t in problem.times]
        self.pending_arrivals = set(range(self.n_processes))
        self.pending_completion = set()
        self.is_solved = False

    def solve(self) -> List[Tuple[int, int]]:
        """Solves for finish and wait times

        :return: List of (finish time, wait time) pairs
        :rtype: List[Tuple[int, int]]
        """
        # Error if already solved
        if self.is_solved:
            raise Exception('problem has been solved')

        if self.problem.method == SchedulingMethod.FCFS:
            self.__log_FCFS()
        elif self.problem.method == SchedulingMethod.SJF:
            self.__log_SJF()
        elif self.problem.method == SchedulingMethod.SRTF:
            self.__log_SRTF()
        elif self.problem.method == SchedulingMethod.RR:
            self.__log_RR()
            pass

        res = self.logger.solve()
        self.is_solved = True

        return res

    def __log_FCFS(self):
        """Logs events using first come, first served
        """
        process_q = []

        # Find start point
        curr_p, curr_t = self.__find_next_arrival()
        self.pending_arrivals.remove(curr_p)
        self.pending_completion.add(curr_p)

        # Log
        self.logger.begin_event(curr_t)
        self.logger.add(curr_p, self.time_left[curr_p])
        self.logger.end_event()

        # Process events
        while len(self.pending_completion) + len(self.pending_arrivals) > 0:
            # Find next event
            next_arrival_p, next_arrival_t = self.__find_next_arrival()
            finish_curr_t = curr_t + self.time_left[curr_p]

            next_t = min(next_arrival_t, finish_curr_t)

            # Update times
            dt = next_t - curr_t
            self.time_left[curr_p] -= dt
            curr_t += dt

            if next_t == next_arrival_t:
                # Next event is process arrival

                # Update sets and queue
                self.pending_arrivals.remove(next_arrival_p)
                self.pending_completion.add(next_arrival_p)
                process_q.append(next_arrival_p)

                # Log
                self.logger.begin_event(curr_t)
                self.logger.add(curr_p, self.time_left[curr_p])
                self.logger.add(next_arrival_p, self.time_left[next_arrival_p])
                self.logger.end_event()

            else:
                # Next event is process finish

                self.logger.begin_event(curr_t)

                # Update sets and find next process
                self.logger.add(curr_p, self.time_left[curr_p])
                self.pending_completion.remove(curr_p)

                # Find next process if still more processes
                if len(self.pending_completion) + len(self.pending_arrivals) > 0:
                    next_p = process_q.pop(0)
                    self.logger.add(next_p, self.time_left[next_p])
                    curr_p = next_p

                self.logger.end_event()

    def __log_SJF(self):
        """Logs events using shortest job first
        """
        # Find start point
        curr_p, curr_t = self.__find_next_arrival()
        self.pending_arrivals.remove(curr_p)
        self.pending_completion.add(curr_p)

        # Log
        self.logger.begin_event(curr_t)
        self.logger.add(curr_p, self.time_left[curr_p])
        self.logger.end_event()

        # Process events
        while len(self.pending_completion) + len(self.pending_arrivals) > 0:
            # Find next event
            next_arrival_p, next_arrival_t = self.__find_next_arrival()
            finish_curr_t = curr_t + self.time_left[curr_p]

            next_t = min(next_arrival_t, finish_curr_t)

            # Update times
            dt = next_t - curr_t
            self.time_left[curr_p] -= dt
            curr_t += dt

            if next_t == next_arrival_t:
                # Next event is process arrival

                # Update sets
                self.pending_arrivals.remove(next_arrival_p)
                self.pending_completion.add(next_arrival_p)

                # Log
                self.logger.begin_event(curr_t)
                self.logger.add(curr_p, self.time_left[curr_p])
                self.logger.add(next_arrival_p, self.time_left[next_arrival_p])
                self.logger.end_event()

            else:
                # Next event is process finish

                self.logger.begin_event(curr_t)

                # Update sets and find next process
                self.logger.add(curr_p, self.time_left[curr_p])
                self.pending_completion.remove(curr_p)

                # Find next process with smallest wait time if still more processes
                # Wait time equivalent to execution time since no interleaving
                if len(self.pending_completion) + len(self.pending_arrivals) > 0:
                    next_p = self.__find_next_shortest()
                    self.logger.add(next_p, self.time_left[next_p])
                    curr_p = next_p

                self.logger.end_event()

    def __log_SRTF(self):
        """Logs events using shortest remaining time first
        """
        # Find start point
        curr_p, curr_t = self.__find_next_arrival()
        self.pending_arrivals.remove(curr_p)
        self.pending_completion.add(curr_p)

        # Log
        self.logger.begin_event(curr_t)
        self.logger.add(curr_p, self.time_left[curr_p])
        self.logger.end_event()

        # Process events
        while len(self.pending_completion) + len(self.pending_arrivals) > 0:
            # Find next event
            next_arrival_p, next_arrival_t = self.__find_next_arrival()
            finish_curr_t = curr_t + self.time_left[curr_p]

            next_t = min(next_arrival_t, finish_curr_t)

            # Update times
            dt = next_t - curr_t
            self.time_left[curr_p] -= dt
            curr_t += dt

            if next_t == next_arrival_t:
                # Next event is process arrival

                # Update sets
                self.pending_arrivals.remove(next_arrival_p)
                self.pending_completion.add(next_arrival_p)

                # Log
                self.logger.begin_event(curr_t)
                self.logger.add(curr_p, self.time_left[curr_p])
                self.logger.add(next_arrival_p, self.time_left[next_arrival_p])
                self.logger.end_event()

                # Switch if remaining time of new arrival is less
                if self.time_left[next_arrival_p] < self.time_left[curr_p]:
                    curr_p = next_arrival_p

            else:
                # Next event is process finish

                self.logger.begin_event(curr_t)

                # Update sets and find next process
                self.logger.add(curr_p, self.time_left[curr_p])
                self.pending_completion.remove(curr_p)

                # Find next process with smallest wait time if still more processes
                if len(self.pending_completion) + len(self.pending_arrivals) > 0:
                    next_p = self.__find_next_shortest()
                    self.logger.add(next_p, self.time_left[next_p])
                    curr_p = next_p

                self.logger.end_event()

    def __log_RR(self):
        """Logs events using round robin
        """
        process_q = []
        time_remaining = self.problem.quantum

        # Find start point
        curr_p, curr_t = self.__find_next_arrival()
        self.pending_arrivals.remove(curr_p)
        self.pending_completion.add(curr_p)

        # Log
        self.logger.begin_event(curr_t)
        self.logger.add(curr_p, self.time_left[curr_p])
        self.logger.end_event()

        # Process events
        while len(self.pending_completion) + len(self.pending_arrivals) > 0:
            # Find next event
            next_arrival_p, next_arrival_t = self.__find_next_arrival()
            finish_curr_t = curr_t + self.time_left[curr_p]
            time_up_t = curr_t + time_remaining

            next_t = min(next_arrival_t, finish_curr_t, time_up_t)

            # Update times
            dt = next_t - curr_t
            self.time_left[curr_p] -= dt
            time_remaining -= dt
            curr_t += dt

            if next_t == next_arrival_t:
                # Next event is process arrival

                # Update sets and queue
                self.pending_arrivals.remove(next_arrival_p)
                self.pending_completion.add(next_arrival_p)
                process_q.append(next_arrival_p)

                # Log
                self.logger.begin_event(curr_t)
                self.logger.add(curr_p, self.time_left[curr_p])
                self.logger.add(next_arrival_p, self.time_left[next_arrival_p])
                self.logger.end_event()

            elif next_t == finish_curr_t:
                # Next event is process finish

                # Reset time remaining
                time_remaining = self.problem.quantum

                # Update sets and find next process
                self.pending_completion.remove(curr_p)

                # Log
                self.logger.begin_event(curr_t)
                self.logger.add(curr_p, self.time_left[curr_p])

                # Find next process if still more processes
                if len(self.pending_completion) + len(self.pending_arrivals) > 0:
                    next_p = process_q.pop(0)
                    self.logger.add(next_p, self.time_left[next_p])
                    curr_p = next_p

                self.logger.end_event()

            else:
                # Next event is time up

                # Reset time remaining
                time_remaining = self.problem.quantum

                # Update queue and find next process
                process_q.append(curr_p)
                next_p = process_q.pop(0)

                # Log
                self.logger.begin_event(curr_t)
                self.logger.add(curr_p, self.time_left[curr_p])
                self.logger.add(next_p, self.time_left[next_p])
                self.logger.end_event()

                curr_p = next_p

    def __find_next_arrival(self) -> Tuple[int, int]:
        """Find next arriving process

        :return: (process, arrival time) pair
        :rtype: Tuple[int, int]
        """
        pending_times = [self.problem.times[i] for i in self.pending_arrivals]
        best_t = float('inf')
        best_p = None
        for p, p_times in zip(self.pending_arrivals, pending_times):
            if p_times[0] < best_t:
                best_p = p
                best_t = p_times[0]
        return best_p, best_t

    def __find_next_shortest(self) -> int:
        """Find next process pending completion with shortest time left

        :return: Process index of next process
        :rtype: int
        """
        wait_times = [
            self.time_left[i] for i in self.pending_completion
        ]
        next_p = min(
            zip(self.pending_completion, wait_times),
            key=lambda pair: pair[1],
        )[0]
        return next_p
