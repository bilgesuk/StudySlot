"""Command-line interface for StudySlot."""

import argparse
from datetime import date
from pathlib import Path
import sys

from studyplanner.planner import clean_text, make_plan, parse_date, positive_int
from studyplanner.storage import load, save


def positive(value):
    try:
        return positive_int(int(value))
    except ValueError:
        raise argparse.ArgumentTypeError("Use a positive whole number.") from None


def calendar_date(value):
    try:
        return parse_date(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from None


def parser():
    root = argparse.ArgumentParser(description="StudySlot: plan study time before deadlines.")
    root.add_argument("--data", type=Path, default=Path("data/tasks.json"),
                      help="Task database (default: data/tasks.json); place before the command.")
    commands = root.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="Add an unfinished task.")
    add.add_argument("--course", required=True)
    add.add_argument("--title", required=True)
    add.add_argument("--due", required=True, type=calendar_date)
    add.add_argument("--minutes", required=True, type=positive)
    commands.add_parser("list", help="List all tasks and their IDs.")
    for name in ("done", "reopen"):
        action = commands.add_parser(name, help=f"{name.capitalize()} a task by ID.")
        action.add_argument("--id", required=True, type=positive)
    plan = commands.add_parser("plan", help="Generate a plan without changing tasks.")
    plan.add_argument("--start", type=calendar_date, default=date.today())
    plan.add_argument("--days", type=positive, default=7)
    plan.add_argument("--daily-minutes", type=positive, default=120)
    plan.add_argument("--output", type=Path, help="Also export to a new UTF-8 text file.")
    return root


def run(args):
    data = load(args.data)
    if args.command == "add":
        task = {"id": data["next_id"], "course": clean_text(args.course),
                "title": clean_text(args.title), "due": args.due.isoformat(),
                "minutes": args.minutes, "done": False}
        data["tasks"].append(task)
        data["next_id"] += 1
        save(args.data, data)
        print(f"Added task #{task['id']}.")
    elif args.command == "list":
        if not data["tasks"]:
            print("No tasks yet. Use add to create one.")
        for task in sorted(data["tasks"], key=lambda task: (task["due"], task["id"])):
            state = "done" if task["done"] else "pending"
            print(f"#{task['id']} [{state}] {task['course']} | {task['title']} | "
                  f"due {task['due']} | {task['minutes']} min")
    elif args.command in ("done", "reopen"):
        task = next((task for task in data["tasks"] if task["id"] == args.id), None)
        if task is None:
            raise ValueError(f"Task #{args.id} does not exist.")
        task["done"] = args.command == "done"
        save(args.data, data)
        print(f"Task #{args.id}: {'done' if task['done'] else 'pending'}.")
    else:
        sessions, unscheduled = make_plan(data["tasks"], args.start, args.days, args.daily_minutes)
        lines = [f"StudySlot | start {args.start} | {args.days} days | {args.daily_minutes} min/day",
                 "Work is scheduled strictly BEFORE the due date."]
        for session in sessions:
            lines.append(f"{session['date']} | #{session['id']} {session['course']} | "
                         f"{session['title']} | {session['minutes']} min")
        if not sessions:
            lines.append("No study sessions scheduled.")
        lines.append(f"Scheduled total: {sum(session['minutes'] for session in sessions)} min")
        if unscheduled:
            lines.append("UNSCHEDULED WORK:")
            for item in unscheduled:
                lines.append(f"#{item['id']}: {item['minutes']} min | {item['reason']}")
        else:
            lines.append("All pending work fits within this plan.")
        report = "\n".join(lines) + "\n"
        if args.output:
            if args.output.resolve() == args.data.resolve():
                raise ValueError("The report cannot replace the task database.")
            with args.output.open("x", encoding="utf-8") as handle:
                handle.write(report)
        print(report, end="")


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        run(args)
    except (ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
