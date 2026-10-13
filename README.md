# StudySlot

StudySlot is a Python command-line study planner for students juggling several
deadlines and a limited daily study budget. It turns task estimates into daily
study sessions and explicitly reports work that could not be scheduled.

## Key Features

- Deadline-aware scheduling that prioritizes tasks by due date.
- Configurable daily study time limits.
- Automatic splitting of tasks across multiple days.
- Clear reporting of unscheduled work and its reasons.
- Persistent local JSON storage with input validation.
- Task completion and reopening using stable IDs.
- Exportable study plans without overwriting existing files.
- Automated unit tests for scheduling and CLI behavior.

## Requirements and setup

Python 3.10 or newer. No third-party packages, account, or network connection
are required. Open a terminal in this repository. On Windows, replace `python3`
with `py` if needed.

```bash
python3 cli.py --help
python3 cli.py add --course CS101 --title "Python project" --due 2026-10-14 --minutes 180
python3 cli.py add --course MATH --title "Practice questions" --due 2026-10-13 --minutes 90
python3 cli.py list
python3 cli.py plan --start 2026-10-11 --days 3 --daily-minutes 90
python3 cli.py plan --start 2026-10-11 --days 3 --daily-minutes 90 --output study-plan.txt
python3 cli.py done --id 2
python3 cli.py reopen --id 2
```

These fixed dates make the demonstration reproducible. For everyday use, provide
your own deadlines and omit `--start` to use the computer's local date. The two
example tasks fit exactly into three 90-minute days. Repeating the plan with
`--daily-minutes 60` leaves 90 minutes of project work unscheduled.

## Commands

| Command | Purpose |
| --- | --- |
| `add --course TEXT --title TEXT --due YYYY-MM-DD --minutes N` | Store a task with its total estimated effort |
| `list` | Show pending and completed tasks with stable IDs |
| `done --id N` | Mark a whole task complete |
| `reopen --id N` | Make a task pending again |
| `plan --start YYYY-MM-DD --days N --daily-minutes N` | Generate a deterministic daily plan |
| `plan ... --output FILE` | Also write the report to a new file; existing files are never overwritten |

Use `python3 cli.py --data /path/to/tasks.json COMMAND ...` for a separate
database. The global `--data` option goes before the command. The default path,
`data/tasks.json`, is relative to the terminal's working directory.

## Scheduling rules and technical explanation

1. Ignore completed tasks.
2. Sort pending tasks by deadline, then task ID for reproducible ties.
3. Visit each day in the requested horizon.
4. Assign its available minutes to the earliest eligible task, splitting work
   across days when necessary.
5. Report every remaining minute and explain why it was not assigned.

```python
minutes = min(capacity, remaining[task["id"]])
remaining[task["id"]] -= minutes
capacity -= minutes
```

The minimum prevents a session from exceeding either the day's remaining capacity
or the task's remaining work. The surrounding loops automate distribution across
days and tasks. Dictionaries track remaining minutes by task ID; functions
separate scheduling, persistence, and command-line interaction.

The due date is **excluded**: a task due on October 14 must be studied by October
13. Past deadlines and deadlines on the start date receive no sessions. A short
horizon may leave work unplanned even when its later deadline remains achievable;
the report distinguishes this from insufficient capacity before a deadline.

Assumptions: all tasks are ready at the start, work can be divided into individual
minutes, and every day (including weekends) has the same capacity. There are no
task dependencies or priority weights. Estimates are provided by the student.
For T tasks and D days, scheduling takes O(T log T + D*T) time; output size is at
most O(D*T). Horizons are limited to 366 days and capacity to 1440 minutes/day.

## Persistence and robustness

The UTF-8 JSON database stores a schema version, the next stable ID, and tasks.
Loading validates the schema, IDs, types, dates, and text. Invalid data causes a
clear error instead of resetting the database. Saving writes a temporary file
in the same directory and atomically replaces the destination to reduce the
risk of partial writes. This is not a backup system.

Input errors return exit code 2 for argparse validation or 1 for application/file
errors; successful commands return 0. A plan with unscheduled work is still a
successful report. Export refuses to overwrite an existing file or the database.
Numeric arguments (`--minutes`, `--days`, `--daily-minutes`, and `--id`) must
contain only ASCII digits `0` through `9` and represent a value greater than zero.
For example, use `10` or `1000`; signs (`+10`), separators (`1_000`), decimals
(`1.5`), and non-ASCII digits are rejected. The planning limits above still apply.
Task titles and course names must be printable, nonempty, and at most 120 characters.

Limitations: local, single-user, sequential CLI use only; simultaneous writes are
not locked and can lose updates. Planning does not mean work was completed and
does not change the stored effort. Partial progress tracking is not implemented;
`done` applies to an entire task. Large or adversarially oversized databases are
not a supported workload. Local data is unencrypted.

## Repository map

| File or folder | Purpose |
| --- | --- |
| `cli.py` | Argument parsing, commands, readable reports, error handling |
| `studyplanner/__init__.py` | Python package marker |
| `studyplanner/planner.py` | Input helpers and scheduling algorithm |
| `studyplanner/storage.py` | JSON validation, loading, and atomic saving |
| `tests/test_planner.py` | Algorithm, CLI lifecycle, and failure-mode tests |
| `.gitignore` | Exclude generated data, Python caches, and the default report |
| `README.md` | Setup, usage, design, limits, and submission checklist |
| `contributions/` | Individual member details and actual contribution records |

`data/` is created on the first successful default-path write and is not committed.

## Verification

```bash
python3 -m unittest discover -s tests -v
```

Tests use temporary directories and do not modify personal task data. They cover
deadline ordering, splitting, capacity, excluded due dates, completed tasks, short
horizons, malformed databases, invalid input, export protection, and task lifecycle.

## Team members

| Name | GitHub | Contributions |
| --- | --- | --- |
| Bilgesu Karakurum | [bilgesuk](https://github.com/bilgesuk) | [Contribution record](contributions/BILGESU_KARAKURUM_2309111044_bilgesuk.md) |
| Ayşe Sude Şirin | [sudesirinn](https://github.com/sudesirinn) | [Contribution record](contributions/AYSE_SUDE_SIRIN_2309011078_sudesirinn.md) |
| Arda Duman | [ardaduman001](https://github.com/ardaduman001) | [Contribution record](contributions/ARDA_DUMAN_2309111032_ardaduman001.md) |
| Arian Haidary | [diabolic67](https://github.com/diabolic67) | [Contribution record](contributions/ARIAN_HAIDARY_2409015555_diabolic67.md) |
| Abderraouf Achour | [raouf0510](https://github.com/raouf0510) | [Contribution record](contributions/ABDERRAOUF_ACHOUR_2409115742_raouf0510.md) |

## Submission status

The implementation is published at https://github.com/bilgesuk/StudySlot.
The English presentation has been completed separately for the homework upload.
The team completed documentation, input-validation, and scheduling reviews
and discussed them verbally. Individual contribution files describe those
reviews and the direct contributions made on October 12, 2026: Sude added the
Key Features section, Abderraouf tightened CLI numeric validation, and Arian
updated his displayed GitHub username and added two planning tests. Arda directly
updated his contribution record in commit `563ea45`, confirming his local
input-validation review and test-suite verification. A follow-up review with
Codex assistance clarified exit codes and the scope of non-ASCII numeric-input
validation, and added independently checked command examples to his record. Bilgesu
coordinates integration with AI assistance, including the follow-up test
indentation and profile-link fixes. On October 13, 2026, Bilgesu confirmed that
presentation preparation is complete and Arian is ready to present.

The initial implementation, tests, documentation, and presentation draft were
created with AI assistance. Team members should review and understand the work,
and follow any applicable course disclosure requirements.
