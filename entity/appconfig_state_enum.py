from enum import Enum


class AppconfigState(Enum):
    COMPLETE = "COMPLETE"
    ROLLED_BACK = "ROLLED_BACK"
    VERIFY_ERROR = "VERIFY_ERROR"
    ERROR = "ERROR"
    NO_CHANGED = "NO_CHANGED"
