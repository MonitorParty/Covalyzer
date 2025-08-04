# modes.py
from enum import Enum


class CoverageMode(Enum):
    ALL_TESTCASES = "all"
    QUEUE_ONLY = "queue"
    QUEUE_WITH_RESTARTS = "queue_restarts"
    ALL_WITH_RESTARTS = "all_restarts"
    FUZZBENCH_LIKE = "fuzzbench"
    EVAL_ONLY = "eval_only"
