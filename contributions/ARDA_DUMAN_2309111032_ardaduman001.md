# Arda Duman

- Student ID: 2309111032
- GitHub: [ardaduman001](https://github.com/ardaduman001)

## Completed contribution: input-validation review

Reviewed the application's handling of invalid input and discussed the expected
behavior with the team verbally. The review covered negative study durations,
invalid calendar dates, and operations on a nonexistent task ID.

Review scope: CLI argument validation and error reporting in `cli.py`, together
with input-validation helpers in `studyplanner/planner.py`.

## Contribution record and verification

Arda updated this record directly in commit `563ea45`, confirming his local
input-validation review and test-suite verification.

- Confirmed CLI exit codes: argument-parsing errors return 2, application or
  file errors return 1, and successful execution returns 0. Invalid numeric
  arguments and calendar dates return 2; blank titles and nonexistent task IDs
  return 1.
- Verified edge cases locally, including non-ASCII digits in numeric arguments
  and negative numbers. Printable non-ASCII text, such as Turkish characters,
  is accepted in course names and task titles.
- Verified the test suite passes locally with
  `python3 -m unittest discover -s tests -v`.
- Presentation preparation is complete, as confirmed by Bilgesu on October 13,
  2026; Arian is ready to present.

### Follow-up verification examples

The following cases were independently checked with Codex assistance on
October 13, 2026, using a temporary database. They document the follow-up review,
not a reconstructed log of Arda's original commands. Each command uses
`python3 cli.py --data <temporary-database>`, followed by the arguments below.

| Arguments | Expected and observed exit code |
| --- | --- |
| `add --course CS101 --title Practice --due 2026-10-14 --minutes -10` | 2 |
| `add --course CS101 --title Practice --due 2026-10-14 --minutes ١٠` | 2 |
| `add --course CS101 --title Practice --due 2026-02-30 --minutes 10` | 2 |
| `add --course CS101 --title "   " --due 2026-10-14 --minutes 10` | 1 |
| `done --id 999` (ID absent from the database) | 1 |
| `add --course Türkçe --title Çalışma --due 2026-10-14 --minutes 10` | 0 |
