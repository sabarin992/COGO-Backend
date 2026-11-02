from datetime import date, timedelta
from typing import List, Union, Set
from app.models.recurring_ride import RecurrenceType

WEEKDAY_NAME_MAP = {
    "monday": 0, "mon": 0,
    "tuesday": 1, "tue": 1,
    "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3,
    "friday": 4, "fri": 4,
    "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6,
}


def normalize_weekdays(weekdays: List[Union[int, str]]) -> Set[int]:
    """Convert a list of ints or string day names to a set of 0-6 integers."""
    result: Set[int] = set()
    if not weekdays:
        return result
    for w in weekdays:
        if isinstance(w, int):
            if 0 <= w <= 6:
                result.add(w)
        elif isinstance(w, str):
            clean = w.strip().lower()
            if clean in WEEKDAY_NAME_MAP:
                result.add(WEEKDAY_NAME_MAP[clean])
            elif clean.isdigit():
                val = int(clean)
                if 0 <= val <= 6:
                    result.add(val)
    return result


def calculate_recurrence_dates(
    recurrence_type: Union[RecurrenceType, str],
    start_date: date,
    end_date: date,
    selected_weekdays: List[Union[int, str]] | None = None,
    working_days: int | None = None,
    off_days: int | None = None,
    shift_start_date: date | None = None,
    min_date: date | None = None,
) -> List[date]:
    """
    Calculates all active journey dates for a recurring ride pattern.
    
    - ONCE: Generates a single ride on start_date
    - DAILY: Generates rides every calendar day in [start_date, end_date]
    - WEEKDAYS: Generates rides Mon-Fri (excludes Sat & Sun)
    - SHIFT: Configurable rotating shift schedule (working_days on, off_days off)
    - CUSTOM: Selected weekdays only
    
    If min_date is given (defaults to None, or today to exclude past dates),
    any dates before min_date are skipped.
    """
    if isinstance(recurrence_type, RecurrenceType):
        rtype = recurrence_type.value.upper()
    else:
        rtype = str(recurrence_type).upper()

    if end_date < start_date:
        return []

    # Handle ONCE
    if rtype == RecurrenceType.ONCE.value:
        if min_date and start_date < min_date:
            return []
        return [start_date]

    generated_dates: List[date] = []
    current = start_date
    one_day = timedelta(days=1)

    # Pre-computations for speed
    custom_weekday_set: Set[int] = set()
    if rtype == RecurrenceType.CUSTOM.value:
        custom_weekday_set = normalize_weekdays(selected_weekdays or [])

    shift_cycle = 0
    if rtype == RecurrenceType.SHIFT.value:
        w_days = working_days or 1
        o_days = off_days or 1
        shift_cycle = w_days + o_days
        shift_anchor = shift_start_date or start_date

    while current <= end_date:
        # Skip past dates if min_date specified
        if min_date and current < min_date:
            current += one_day
            continue

        if rtype == RecurrenceType.DAILY.value:
            generated_dates.append(current)

        elif rtype == RecurrenceType.WEEKDAYS.value:
            # 0=Monday, 4=Friday, 5=Saturday, 6=Sunday
            if current.weekday() < 5:
                generated_dates.append(current)

        elif rtype == RecurrenceType.SHIFT.value:
            offset = (current - shift_anchor).days
            cycle_pos = offset % shift_cycle
            if 0 <= cycle_pos < (working_days or 1):
                generated_dates.append(current)

        elif rtype == RecurrenceType.CUSTOM.value:
            if current.weekday() in custom_weekday_set:
                generated_dates.append(current)

        current += one_day

    return generated_dates
