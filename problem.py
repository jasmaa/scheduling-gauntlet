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

    def solve(self) -> List[Tuple[int, int]]:
        """Solves for finish and wait times

        :return: List of (finish time, wait time) pairs
        :rtype: List[Tuple[int, int]]
        """
        if self.method == SchedulingMethod.FCFS:
            return self.__solve_FCFS()
        elif self.method == SchedulingMethod.SRTF:
            return self.__solve_SRTF()

    def __solve_FCFS(self):
        pass

    def __solve_SRTF(self):
        """Solves SRTF problem
        """
        n_processes = len(self.times)

        events = []
        time_left = [exec_t for _, exec_t in self.times]
        pending_arrivals = set(range(n_processes))
        pending_completion = set()

        def find_next_arrival():
            """Helper to find next arrival from pending processes
            """
            pending_times = [self.times[i] for i in pending_arrivals]
            best_t = float('inf')
            best_p = None
            for p, p_times in zip(pending_arrivals, pending_times):
                if p_times[0] < best_t:
                    best_p = p
                    best_t = p_times[0]
            return best_p, best_t

        def find_next_pending_completion():
            wait_times = [time_left[i] for i in pending_completion]
            best_t = float('inf')
            best_p = None
            for p, t in zip(pending_completion, wait_times):
                if t < best_t:
                    best_p = p
                    best_t = t
            return best_p, best_t

        # Find start point
        curr_p, curr_t = find_next_arrival()
        pending_arrivals.remove(curr_p)
        pending_completion.add(curr_p)

        # Log
        event_state = [None] * n_processes
        event_state[curr_p] = time_left[curr_p]
        events.append((curr_t, event_state))

        # Process events
        while len(pending_completion) + len(pending_arrivals) > 0:
            # Find next event
            next_arrival_p, next_arrival_t = find_next_arrival()
            finish_curr_t = curr_t + time_left[curr_p]

            if next_arrival_t < finish_curr_t:
                # Next event is process arrival
                dt = next_arrival_t - curr_t
                time_left[curr_p] -= dt
                curr_t += dt

                # Update sets
                pending_arrivals.remove(next_arrival_p)
                pending_completion.add(next_arrival_p)

                # Log
                event_state = [None] * n_processes
                event_state[curr_p] = time_left[curr_p]
                event_state[next_arrival_p] = time_left[next_arrival_p]
                events.append((curr_t, event_state))

                # Switch if remaining time of new arrival is less
                if time_left[next_arrival_p] < time_left[curr_p]:
                    curr_p = next_arrival_p

            else:
                # Next event is process finish
                dt = finish_curr_t - curr_t
                time_left[curr_p] -= dt
                curr_t += dt

                event_state = [None] * n_processes

                # Update sets and find next process
                event_state[curr_p] = time_left[curr_p]
                pending_completion.remove(curr_p)

                # Find next process if still more processes
                if len(pending_completion) + len(pending_arrivals) > 0:
                    next_p, next_t = find_next_pending_completion()
                    event_state[next_p] = time_left[next_p]
                    curr_p = next_p

                # Log
                events.append((curr_t, event_state))

        # Determine finish and wait times from event log
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


p = Problem(SchedulingMethod.SRTF, [
    (0, 9),
    (1, 4),
    (2, 9),
])

pprint(p.solve())
