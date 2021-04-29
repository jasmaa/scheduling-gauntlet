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
        :type qauntum: int
        """
        self.method = method
        self.times = times
        self.quantum = quantum

    def solve() -> List[Tuple[int, int]]:
        """Solves for finish and wait times

        :return: List of (finish time, wait time) pairs
        :rtype: List[Tuple[int, int]]
        """
        pass
