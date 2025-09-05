"""
Shared types and constants for Atlas Toolset MCP
"""

from enum import Enum
from typing import Literal, Union


class Priority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"
    
    @classmethod
    def values(cls):
        return [p.value for p in cls]


class TaskStatus(str, Enum):
    """Task status values"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ARCHIVED = "archived"
    
    @classmethod
    def values(cls):
        return [s.value for s in cls]


class DateFormat(str, Enum):
    """Date format options"""
    ITALIAN = "DD/MM/YYYY"
    ISO = "YYYY-MM-DD"
    US = "MM/DD/YYYY"
    FULL_ITALIAN = "DD/MM/YYYY HH:mm:ss"
    TIMESTAMP = "YYYY-MM-DD HH:mm:ss"


class TimeUnit(str, Enum):
    """Time units for calculations"""
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"
    
    @classmethod
    def values(cls):
        return [u.value for u in cls]


class MathOperation(str, Enum):
    """Mathematical operations"""
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    POWER = "power"
    MODULO = "modulo"
    SQRT = "sqrt"
    FACTORIAL = "factorial"
    PERCENTAGE = "percentage"
    AVERAGE = "average"
    
    @classmethod
    def values(cls):
        return [op.value for op in cls]


class TextAnalysisMode(str, Enum):
    """Text analysis modes"""
    BASIC = "basic"
    DETAILED = "detailed"
    READABILITY = "readability"
    SENTIMENT = "sentiment"
    KEYWORDS = "keywords"
    
    @classmethod
    def values(cls):
        return [m.value for m in cls]


# Type aliases for clarity
DateShortcut = Literal["now", "yesterday", "tomorrow", "last_month", "next_month", "EoD", "EoM"]
CalculatorMode = Literal["basic", "scientific", "statistical", "financial"]
