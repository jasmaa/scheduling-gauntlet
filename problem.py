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

        pprint(self.events)

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
            logger = self.__log_SRTF()
        elif self.method == SchedulingMethod.SRTF:
            logger = self.__log_SRTF()

        return logger.solve()

    def __log_FCFS(self):
        """Solves first come, first served problem
        """
        pass

    def __log_SRTF(self) -> EventLogger:
        """Logs events using shortest remaining time first

        :return: Event logger
        :rtype: EventLogger
        """
        n_processes = len(self.times)

        logger = EventLogger(n_processes)
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
            """Helper to find next shortest process
            """
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
        logger.begin_event(curr_t)
        logger.add(curr_p, time_left[curr_p])
        logger.end_event()

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
                logger.begin_event(curr_t)
                logger.add(curr_p, time_left[curr_p])
                logger.add(next_arrival_p, time_left[next_arrival_p])
                logger.end_event()

                # Switch if remaining time of new arrival is less
                if time_left[next_arrival_p] < time_left[curr_p]:
                    curr_p = next_arrival_p

            else:
                # Next event is process finish
                dt = finish_curr_t - curr_t
                time_left[curr_p] -= dt
                curr_t += dt

                logger.begin_event(curr_t)

                # Update sets and find next process
                logger.add(curr_p, time_left[curr_p])

                pending_completion.remove(curr_p)

                # Find next process if still more processes
                if len(pending_completion) + len(pending_arrivals) > 0:
                    next_p, next_t = find_next_pending_completion()

                    logger.add(next_p, time_left[next_p])
                    curr_p = next_p

                logger.end_event()

        return logger


p = Problem(SchedulingMethod.SRTF, [
    (0, 9),
    (1, 4),
    (2, 9),
])

pprint(p.solve())
