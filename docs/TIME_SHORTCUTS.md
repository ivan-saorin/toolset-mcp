# Time Shortcuts Quick Reference

## Basic Shortcuts

| Shortcut | Description | Example Result (from 05/09/2025 20:06:00) |
|----------|-------------|-------------------------------------------|
| `now` | Current datetime | 05/09/2025 20:06:00 |
| `yesterday` | 24 hours ago | 04/09/2025 20:06:00 |
| `tomorrow` | 24 hours ahead | 06/09/2025 20:06:00 |
| `last_month` | Same day last month | 05/08/2025 20:06:00 |
| `next_month` | Same day next month | 05/10/2025 20:06:00 |
| `last_week` | 7 days ago | 29/08/2025 20:06:00 |
| `next_week` | 7 days ahead | 12/09/2025 20:06:00 |
| `last_year` | Same date last year | 05/09/2024 20:06:00 |
| `next_year` | Same date next year | 05/09/2026 20:06:00 |

## Time Modifiers

| Modifier | Description | Example |
|----------|-------------|---------|
| `EoD` | End of Day (23:59:59) | 05/09/2025 23:59:59 |
| `EoM` | End of Month | 30/09/2025 20:06:00 |
| `SoD` | Start of Day (00:00:00) | 05/09/2025 00:00:00 |
| `SoM` | Start of Month | 01/09/2025 20:06:00 |

## Compound Shortcuts

You can combine shortcuts for more complex dates:

| Compound | Result |
|----------|--------|
| `tomorrow EoD` | Tomorrow at 23:59:59 |
| `yesterday SoD` | Yesterday at 00:00:00 |
| `next month EoM` | Last day of next month at current time |
| `last month SoM` | First day of last month at current time |
| `tomorrow EoD` | 06/09/2025 23:59:59 |
| `next month EoM` | 31/10/2025 20:06:00 |

## Date Formats

| Format | Example | Description |
|--------|---------|-------------|
| `italian` | 05/09/2025 20:06:00 | DD/MM/YYYY HH:mm:ss |
| `iso` | 2025-09-05T20:06:00 | ISO 8601 format |
| `us` | 09/05/2025 20:06:00 | MM/DD/YYYY HH:mm:ss |
| `timestamp` | 2025-09-05 20:06:00 | YYYY-MM-DD HH:mm:ss |
| `full_italian` | venerdì 5 settembre 2025, 20:06:00 | With day and month names |

## Usage Examples

### Parse Shortcut
```python
result = await time_parse("tomorrow EoD", format="italian")
# Returns: "06/09/2025 23:59:59"
```

### Calculate Time Difference
```python
result = await time_calculate("now", "next month EoM", unit="days")
# Returns: Days until end of next month with detailed statistics
```

### Add Time
```python
result = await time_add("tomorrow", 15, unit="days", format="italian")
# Returns: Date 16 days from now
```

## Date Calculation Statistics

When calculating differences between dates, you get:
- **Total time** in various units (seconds, minutes, hours, days)
- **Breakdown** by years, months, weeks, days, hours, minutes, seconds
- **Working days** (Monday-Friday)
- **Weekend days** (Saturday-Sunday)
- **Week information** (week of year, quarter)
- **Human-readable** difference (e.g., "3 giorni", "2 settimane")

## Italian Month Names
- gennaio, febbraio, marzo, aprile, maggio, giugno
- luglio, agosto, settembre, ottobre, novembre, dicembre

## Italian Day Names
- lunedì, martedì, mercoledì, giovedì, venerdì, sabato, domenica
