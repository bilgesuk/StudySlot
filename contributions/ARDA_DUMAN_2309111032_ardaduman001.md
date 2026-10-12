# Arda Duman

- Student ID: 2309111032
- GitHub: [ardaduman001](https://github.com/ardaduman001)

## Completed contribution: input-validation review

Reviewed the application's handling of invalid input and discussed the expected
behavior with the team verbally. The review covered negative study durations,
invalid calendar dates, and operations on a nonexistent task ID.

Review scope: CLI argument validation and error reporting in `cli.py`, together
with input-validation helpers in `studyplanner/planner.py`.

## Contribution record & Verification

- Confirmed input-validation rules align with CLI exit codes (code 2 for invalid arguments, 0 for successful execution).
- Verified edge cases locally, including non-ASCII inputs and negative numbers.
- Verified test suite passes locally with `python3 -m unittest discover -s tests -v`.
- Presentation slide preparation and team coordination ongoing.
