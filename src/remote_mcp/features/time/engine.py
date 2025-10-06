"""
Time Engine with Italian format and advanced date shortcuts
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta, date
from calendar import monthrange
from ...shared.base import BaseFeature, ToolResponse
from ...shared.types import DateFormat, TimeUnit


class TimeEngine(BaseFeature):
    """Time and date utilities with Italian format and shortcuts"""
    
    def __init__(self):
        super().__init__("time", "2.0.0")
        
        # Italian month names
        self.italian_months = [
            "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
            "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"
        ]
        
        # Italian day names
        self.italian_days = [
            "lunedì", "martedì", "mercoledì", "giovedì", 
            "venerdì", "sabato", "domenica"
        ]
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of time tools"""
        return [
            {
                "name": "time_now",
                "description": "Get current date and time",
                "parameters": {
                    "format": "Format: italian, iso, us, timestamp",
                    "timezone": "Timezone offset in hours"
                }
            },
            {
                "name": "time_parse",
                "description": "Parse date shortcuts like 'tomorrow EoD', 'next month EoM'",
                "parameters": {
                    "shortcut": "Shortcut: now, yesterday, tomorrow, last_month, next_month, EoD, EoM, or combinations",
                    "format": "Output format"
                }
            },
            {
                "name": "time_calculate",
                "description": "Calculate date differences and statistics",
                "parameters": {
                    "date1": "First date (ISO format or shortcut)",
                    "date2": "Second date (ISO format or shortcut)",
                    "unit": "Result unit: days, hours, minutes, etc."
                }
            },
            {
                "name": "time_add",
                "description": "Add or subtract time from a date",
                "parameters": {
                    "base_date": "Base date (ISO format or shortcut)",
                    "amount": "Amount to add (negative to subtract)",
                    "unit": "Unit: days, hours, months, etc."
                }
            },
            {
                "name": "time_format",
                "description": "Convert between date formats",
                "parameters": {
                    "date_input": "Date to format",
                    "input_format": "Input format",
                    "output_format": "Output format"
                }
            }
        ]
    
    def time_now(self, format: str = "italian", timezone: int = 0) -> ToolResponse:
        """
        Get current date and time
        
        Args:
            format: Output format (italian, iso, us, timestamp)
            timezone: Timezone offset in hours
        """
        try:
            # Get current time with timezone offset
            now = datetime.now() + timedelta(hours=timezone)
            
            formatted = self._format_datetime(now, format)
            
            return ToolResponse(
                success=True,
                data={
                    "datetime": formatted,
                    "format": format,
                    "timezone_offset": timezone,
                    "components": {
                        "year": now.year,
                        "month": now.month,
                        "day": now.day,
                        "hour": now.hour,
                        "minute": now.minute,
                        "second": now.second,
                        "weekday": self.italian_days[now.weekday()],
                        "month_name": self.italian_months[now.month - 1]
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error("time_now", e)
    
    def time_parse(self, shortcut: str, format: str = "italian") -> ToolResponse:
        """
        Parse date shortcuts
        
        Args:
            shortcut: Date shortcut (e.g., 'tomorrow EoD', 'next month EoM')
            format: Output format
        """
        try:
            # Parse the shortcut
            result_date = self._parse_shortcut(shortcut)
            
            if result_date is None:
                return ToolResponse(
                    success=False,
                    error=f"Unable to parse shortcut: {shortcut}"
                )
            
            formatted = self._format_datetime(result_date, format)
            
            # Calculate difference from now
            now = datetime.now()
            diff = result_date - now
            
            return ToolResponse(
                success=True,
                data={
                    "shortcut": shortcut,
                    "datetime": formatted,
                    "format": format,
                    "from_now": {
                        "days": diff.days,
                        "hours": int(diff.total_seconds() // 3600),
                        "minutes": int(diff.total_seconds() // 60),
                        "human_readable": self._human_readable_diff(diff)
                    },
                    "components": {
                        "year": result_date.year,
                        "month": result_date.month,
                        "day": result_date.day,
                        "hour": result_date.hour,
                        "minute": result_date.minute,
                        "second": result_date.second,
                        "weekday": self.italian_days[result_date.weekday()],
                        "month_name": self.italian_months[result_date.month - 1]
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error("time_parse", e)
    
    def time_calculate(self, date1: str, date2: str, unit: str = "days") -> ToolResponse:
        """
        Calculate difference between two dates with detailed statistics
        
        Args:
            date1: First date (ISO format or shortcut)
            date2: Second date (ISO format or shortcut)
            unit: Result unit (days, hours, minutes, etc.)
        """
        try:
            # Parse dates
            dt1 = self._parse_date_input(date1)
            dt2 = self._parse_date_input(date2)
            
            if dt1 is None or dt2 is None:
                return ToolResponse(
                    success=False,
                    error="Unable to parse one or both dates"
                )
            
            # Calculate difference
            diff = dt2 - dt1
            total_seconds = diff.total_seconds()
            
            # Convert to requested unit
            conversions = {
                "seconds": total_seconds,
                "minutes": total_seconds / 60,
                "hours": total_seconds / 3600,
                "days": total_seconds / 86400,
                "weeks": total_seconds / 604800,
                "months": total_seconds / 2592000,  # Approximate (30 days)
                "years": total_seconds / 31536000   # Approximate (365 days)
            }
            
            result = conversions.get(unit, total_seconds)
            
            # Calculate comprehensive statistics
            stats = {
                "total_seconds": int(total_seconds),
                "total_minutes": int(total_seconds / 60),
                "total_hours": int(total_seconds / 3600),
                "total_days": int(total_seconds / 86400),
                "breakdown": {
                    "years": int(total_seconds // 31536000),
                    "months": int((total_seconds % 31536000) // 2592000),
                    "weeks": int((total_seconds % 2592000) // 604800),
                    "days": int((total_seconds % 604800) // 86400),
                    "hours": int((total_seconds % 86400) // 3600),
                    "minutes": int((total_seconds % 3600) // 60),
                    "seconds": int(total_seconds % 60)
                },
                "working_days": self._calculate_working_days(dt1, dt2),
                "weekends": self._calculate_weekends(dt1, dt2)
            }
            
            return ToolResponse(
                success=True,
                data={
                    "date1": self._format_datetime(dt1, "italian"),
                    "date2": self._format_datetime(dt2, "italian"),
                    "difference": {
                        "value": result,
                        "unit": unit,
                        "is_future": dt2 > dt1,
                        "human_readable": self._human_readable_diff(diff)
                    },
                    "statistics": stats,
                    "date1_info": {
                        "weekday": self.italian_days[dt1.weekday()],
                        "is_weekend": dt1.weekday() >= 5,
                        "quarter": (dt1.month - 1) // 3 + 1,
                        "week_of_year": dt1.isocalendar()[1]
                    },
                    "date2_info": {
                        "weekday": self.italian_days[dt2.weekday()],
                        "is_weekend": dt2.weekday() >= 5,
                        "quarter": (dt2.month - 1) // 3 + 1,
                        "week_of_year": dt2.isocalendar()[1]
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error("time_calculate", e)
    
    def time_add(self, base_date: str, amount: float, unit: str = "days", 
                 format: str = "italian") -> ToolResponse:
        """
        Add or subtract time from a date
        
        Args:
            base_date: Base date (ISO format or shortcut)
            amount: Amount to add (negative to subtract)
            unit: Unit (days, hours, months, etc.)
            format: Output format
        """
        try:
            # Parse base date
            dt = self._parse_date_input(base_date)
            if dt is None:
                return ToolResponse(
                    success=False,
                    error=f"Unable to parse date: {base_date}"
                )
            
            # Calculate new date
            if unit == "seconds":
                new_dt = dt + timedelta(seconds=amount)
            elif unit == "minutes":
                new_dt = dt + timedelta(minutes=amount)
            elif unit == "hours":
                new_dt = dt + timedelta(hours=amount)
            elif unit == "days":
                new_dt = dt + timedelta(days=amount)
            elif unit == "weeks":
                new_dt = dt + timedelta(weeks=amount)
            elif unit == "months":
                # Handle month addition carefully
                new_dt = self._add_months(dt, int(amount))
            elif unit == "years":
                # Handle year addition
                try:
                    new_dt = dt.replace(year=dt.year + int(amount))
                except ValueError:
                    # Handle leap year edge case (Feb 29)
                    new_dt = dt.replace(year=dt.year + int(amount), day=28)
            else:
                return ToolResponse(
                    success=False,
                    error=f"Unknown unit: {unit}"
                )
            
            formatted = self._format_datetime(new_dt, format)
            
            return ToolResponse(
                success=True,
                data={
                    "original_date": self._format_datetime(dt, format),
                    "operation": f"{'+' if amount >= 0 else ''}{amount} {unit}",
                    "result_date": formatted,
                    "format": format,
                    "difference_from_now": {
                        "days": (new_dt - datetime.now()).days,
                        "human_readable": self._human_readable_diff(new_dt - datetime.now())
                    },
                    "result_info": {
                        "weekday": self.italian_days[new_dt.weekday()],
                        "is_weekend": new_dt.weekday() >= 5,
                        "month_name": self.italian_months[new_dt.month - 1],
                        "quarter": (new_dt.month - 1) // 3 + 1,
                        "is_leap_year": self._is_leap_year(new_dt.year)
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error("time_add", e)
    
    def time_format(self, date_input: str, input_format: str = "auto", 
                   output_format: str = "italian") -> ToolResponse:
        """
        Convert between date formats
        
        Args:
            date_input: Date to format
            input_format: Input format (auto-detect if 'auto')
            output_format: Output format
        """
        try:
            # Parse input
            if input_format == "auto":
                dt = self._parse_date_input(date_input)
            else:
                dt = self._parse_with_format(date_input, input_format)
            
            if dt is None:
                return ToolResponse(
                    success=False,
                    error=f"Unable to parse date: {date_input}"
                )
            
            # Format output
            formatted = self._format_datetime(dt, output_format)
            
            # Also provide in multiple formats for convenience
            formats = {
                "italian": self._format_datetime(dt, "italian"),
                "iso": self._format_datetime(dt, "iso"),
                "us": self._format_datetime(dt, "us"),
                "timestamp": self._format_datetime(dt, "timestamp"),
                "full_italian": self._format_datetime(dt, "full_italian")
            }
            
            return ToolResponse(
                success=True,
                data={
                    "input": date_input,
                    "output": formatted,
                    "requested_format": output_format,
                    "all_formats": formats,
                    "date_info": {
                        "year": dt.year,
                        "month": dt.month,
                        "day": dt.day,
                        "hour": dt.hour,
                        "minute": dt.minute,
                        "second": dt.second,
                        "weekday": self.italian_days[dt.weekday()],
                        "month_name": self.italian_months[dt.month - 1],
                        "is_weekend": dt.weekday() >= 5,
                        "day_of_year": dt.timetuple().tm_yday,
                        "week_of_year": dt.isocalendar()[1]
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error("time_format", e)
    
    def _parse_shortcut(self, shortcut: str) -> datetime]:
        """
        Parse date shortcuts including combinations like 'tomorrow EoD'
        
        Shortcuts:
        - now: current datetime
        - yesterday/tomorrow: +/- 1 day at same time
        - last_month/next_month: +/- 1 month at same time
        - EoD: End of Day (23:59:59)
        - EoM: End of Month at same time
        - Combinations: 'tomorrow EoD', 'next month EoM', etc.
        """
        shortcut = shortcut.lower().strip()
        now = datetime.now()
        result = now
        
        # Track if any valid keyword was found
        valid_keyword_found = False
        
        # Split shortcut into parts
        parts = shortcut.split()
        
        for part in parts:
            if part == "now":
                result = now
                valid_keyword_found = True
            elif part == "yesterday":
                result = result - timedelta(days=1)
                valid_keyword_found = True
            elif part == "tomorrow":
                result = result + timedelta(days=1)
                valid_keyword_found = True
            elif part == "last_month" or part == "last month":
                result = self._add_months(result, -1)
                valid_keyword_found = True
            elif part == "next_month" or part == "next month":
                result = self._add_months(result, 1)
                valid_keyword_found = True
            elif part == "eod" or part == "end_of_day":
                result = result.replace(hour=23, minute=59, second=59, microsecond=999999)
                valid_keyword_found = True
            elif part == "eom" or part == "end_of_month":
                # Get last day of the month
                last_day = monthrange(result.year, result.month)[1]
                result = result.replace(day=last_day)
                valid_keyword_found = True
            elif part == "sod" or part == "start_of_day":
                result = result.replace(hour=0, minute=0, second=0, microsecond=0)
                valid_keyword_found = True
            elif part == "som" or part == "start_of_month":
                result = result.replace(day=1)
                valid_keyword_found = True
            elif part == "last_week" or part == "last week":
                result = result - timedelta(weeks=1)
                valid_keyword_found = True
            elif part == "next_week" or part == "next week":
                result = result + timedelta(weeks=1)
                valid_keyword_found = True
            elif part == "last_year" or part == "last year":
                try:
                    result = result.replace(year=result.year - 1)
                    valid_keyword_found = True
                except ValueError:
                    # Handle Feb 29 in leap years
                    result = result.replace(year=result.year - 1, day=28)
                    valid_keyword_found = True
            elif part == "next_year" or part == "next year":
                try:
                    result = result.replace(year=result.year + 1)
                    valid_keyword_found = True
                except ValueError:
                    # Handle Feb 29 in leap years
                    result = result.replace(year=result.year + 1, day=28)
                    valid_keyword_found = True
        
        # Handle compound shortcuts (handle as phrases)
        if "next month eom" in shortcut.lower():
            result = self._add_months(now, 1)
            last_day = monthrange(result.year, result.month)[1]
            result = result.replace(day=last_day)
            valid_keyword_found = True
        elif "tomorrow eod" in shortcut.lower():
            result = now + timedelta(days=1)
            result = result.replace(hour=23, minute=59, second=59, microsecond=999999)
            valid_keyword_found = True
        
        # Only return a result if we found a valid keyword
        return result if valid_keyword_found else None
    
    def _parse_date_input(self, date_input: str) -> datetime]:
        """Parse date input which could be ISO format or a shortcut"""
        # Try common date formats first (more likely than shortcuts)
        date_input = date_input.strip()
        
        # Try common date formats first
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%Y-%m-%dT%H:%M:%S",  # ISO format with T separator
            "%Y-%m-%dT%H:%M:%SZ",  # ISO format with Z
            "%Y-%m-%dT%H:%M:%S.%f",  # ISO format with microseconds
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_input, fmt)
            except ValueError:
                continue
        
        # If no format matches, try parsing as shortcut
        # Only return the shortcut result if it's actually a valid shortcut
        if any(keyword in date_input.lower() for keyword in 
               ['now', 'yesterday', 'tomorrow', 'eod', 'eom', 'last', 'next', 'sod', 'som']):
            return self._parse_shortcut(date_input)
        
        return None
    
    def _parse_with_format(self, date_input: str, format_type: str) -> datetime]:
        """Parse date with specific format"""
        format_map = {
            "italian": "%d/%m/%Y %H:%M:%S",
            "iso": "%Y-%m-%d %H:%M:%S",
            "us": "%m/%d/%Y %H:%M:%S",
            "timestamp": "%Y-%m-%d %H:%M:%S"
        }
        
        fmt = format_map.get(format_type)
        if not fmt:
            return None
        
        try:
            return datetime.strptime(date_input, fmt)
        except ValueError:
            # Try without time
            try:
                fmt_date_only = fmt.split()[0]
                return datetime.strptime(date_input, fmt_date_only)
            except ValueError:
                return None
    
    def _format_datetime(self, dt: datetime, format_type: str) -> str:
        """Format datetime according to specified format"""
        if format_type == "italian":
            return dt.strftime("%d/%m/%Y %H:%M:%S")
        elif format_type == "iso":
            return dt.isoformat()
        elif format_type == "us":
            return dt.strftime("%m/%d/%Y %H:%M:%S")
        elif format_type == "timestamp":
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        elif format_type == "full_italian":
            # Full Italian format with day and month names
            day_name = self.italian_days[dt.weekday()]
            month_name = self.italian_months[dt.month - 1]
            return f"{day_name} {dt.day} {month_name} {dt.year}, {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"
        else:
            return dt.strftime("%d/%m/%Y %H:%M:%S")  # Default to Italian
    
    def _add_months(self, dt: datetime, months: int) -> datetime:
        """Add months to a datetime, handling edge cases"""
        month = dt.month - 1 + months
        year = dt.year + month // 12
        month = month % 12 + 1
        day = min(dt.day, monthrange(year, month)[1])
        
        return dt.replace(year=year, month=month, day=day)
    
    def _human_readable_diff(self, diff: timedelta) -> str:
        """Convert timedelta to human-readable string"""
        total_seconds = abs(diff.total_seconds())
        
        if total_seconds < 60:
            return f"{int(total_seconds)} secondi"
        elif total_seconds < 3600:
            minutes = int(total_seconds / 60)
            return f"{minutes} minuti"
        elif total_seconds < 86400:
            hours = int(total_seconds / 3600)
            return f"{hours} ore"
        elif total_seconds < 604800:
            days = int(total_seconds / 86400)
            return f"{days} giorni"
        elif total_seconds < 2592000:
            weeks = int(total_seconds / 604800)
            return f"{weeks} settimane"
        elif total_seconds < 31536000:
            months = int(total_seconds / 2592000)
            return f"{months} mesi"
        else:
            years = int(total_seconds / 31536000)
            return f"{years} anni"
    
    def _calculate_working_days(self, dt1: datetime, dt2: datetime) -> int:
        """Calculate number of working days between two dates"""
        if dt1 > dt2:
            dt1, dt2 = dt2, dt1
        
        working_days = 0
        current = dt1.date()
        end = dt2.date()
        
        while current <= end:
            if current.weekday() < 5:  # Monday = 0, Friday = 4
                working_days += 1
            current += timedelta(days=1)
        
        return working_days
    
    def _calculate_weekends(self, dt1: datetime, dt2: datetime) -> int:
        """Calculate number of weekend days between two dates"""
        if dt1 > dt2:
            dt1, dt2 = dt2, dt1
        
        weekend_days = 0
        current = dt1.date()
        end = dt2.date()
        
        while current <= end:
            if current.weekday() >= 5:  # Saturday = 5, Sunday = 6
                weekend_days += 1
            current += timedelta(days=1)
        
        return weekend_days
    
    def _is_leap_year(self, year: int) -> bool:
        """Check if a year is a leap year"""
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
