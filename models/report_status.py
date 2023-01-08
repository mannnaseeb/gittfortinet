from . import db
from enum import Enum


class ReportStatus(Enum):
    RUNNING = 2
    GENERATED = 1
    