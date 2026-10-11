"""Validation and deterministic earliest-deadline-first scheduling."""

from datetime import date, timedelta


def parse_date(value):
    try:
        parsed = date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError("Dates must use YYYY-MM-DD and be valid calendar dates.") from None
    if parsed.isoformat() != value:
        raise ValueError("Dates must use YYYY-MM-DD.")
    return parsed


def positive_int(value):
    if type(value) is not int or value <= 0:
        raise ValueError("Expected a positive whole number.")
    return value


def clean_text(value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Course and title must contain text.")
    if len(value) > 120 or any(not char.isprintable() for char in value):
        raise ValueError("Text must be printable and no longer than 120 characters.")
    return value.strip()


def make_plan(tasks, start, days, daily_minutes):
    """Split unfinished tasks across days strictly before each deadline.

    All tasks are available at the start; work is divisible into minutes.
    Planning does not record completed work or modify the input tasks.
    """
    positive_int(days)
    positive_int(daily_minutes)
    if days > 366 or daily_minutes > 1440:
        raise ValueError("Use at most 366 days and 1440 minutes per day.")
    if start.toordinal() + days - 1 > date.max.toordinal():
        raise ValueError("The planning horizon exceeds the supported calendar.")
    pending = sorted(
        (task for task in tasks if not task["done"]),
        key=lambda task: (task["due"], task["id"]),
    )
    remaining = {task["id"]: task["minutes"] for task in pending}
    sessions = []
    for offset in range(days):
        day = start + timedelta(days=offset)
        capacity = daily_minutes
        for task in pending:
            if day >= parse_date(task["due"]) or remaining[task["id"]] == 0:
                continue
            minutes = min(capacity, remaining[task["id"]])
            if minutes:
                sessions.append({"date": day.isoformat(), "id": task["id"],
                                 "course": task["course"], "title": task["title"],
                                 "minutes": minutes})
                remaining[task["id"]] -= minutes
                capacity -= minutes
            if capacity == 0:
                break
    last_day = start + timedelta(days=days - 1)
    unscheduled = []
    for task in pending:
        if remaining[task["id"]]:
            deadline = parse_date(task["due"])
            if deadline <= start:
                reason = "deadline reached before planning starts"
            elif deadline.toordinal() - 1 <= last_day.toordinal():
                reason = "insufficient capacity before deadline"
            else:
                reason = "outside this horizon; extend the plan to assess feasibility"
            unscheduled.append({"id": task["id"], "minutes": remaining[task["id"]],
                                "reason": reason})
    return sessions, unscheduled
