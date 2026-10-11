"""Strict JSON loading and atomic replacement of the local task file."""

import json
import os
from pathlib import Path
import tempfile

from studyplanner.planner import clean_text, parse_date, positive_int


def validate(data):
    if not isinstance(data, dict) or set(data) != {"version", "next_id", "tasks"}:
        raise ValueError("Invalid database structure.")
    if type(data["version"]) is not int or data["version"] != 1:
        raise ValueError("Unsupported database version.")
    positive_int(data["next_id"])
    if not isinstance(data["tasks"], list):
        raise ValueError("Tasks must be a list.")
    ids = set()
    for task in data["tasks"]:
        if not isinstance(task, dict) or set(task) != {"id", "course", "title", "due", "minutes", "done"}:
            raise ValueError("Invalid task structure.")
        positive_int(task["id"])
        positive_int(task["minutes"])
        clean_text(task["course"])
        clean_text(task["title"])
        parse_date(task["due"])
        if type(task["done"]) is not bool or task["id"] in ids:
            raise ValueError("Invalid completion status or duplicate task ID.")
        ids.add(task["id"])
    if ids and data["next_id"] <= max(ids):
        raise ValueError("next_id must be larger than every existing task ID.")
    return data


def load(path):
    path = Path(path)
    try:
        with path.open(encoding="utf-8") as handle:
            return validate(json.load(handle))
    except FileNotFoundError:
        return {"version": 1, "next_id": 1, "tasks": []}
    except (json.JSONDecodeError, UnicodeError, RecursionError):
        raise ValueError("Database is not valid UTF-8 JSON; it has not been changed.") from None


def save(path, data):
    validate(data)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".studyslot-", delete=False) as handle:
            temporary = handle.name
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)
