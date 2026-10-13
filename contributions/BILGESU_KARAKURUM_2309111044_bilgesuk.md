# Bilgesu Karakurum

- Student ID: 2309111044
- GitHub: [bilgesuk](https://github.com/bilgesuk)

## Implementation coordination and review

I selected the study-planning use case and coordinated implementation with AI
assistance. The assistant generated the initial Python implementation, automated
tests, README, and presentation draft. I reviewed explanations of the scheduling
algorithm, JSON persistence, and CLI argument handling.

## Manual verification performed

- Ran `python3 cli.py --help` and checked the available commands.
- Ran the example plan with 90 minutes per day and verified that all 270 minutes
  fit before the deadlines.
- Repeated the plan with 60 minutes per day and confirmed the capacity warning.
- Entered a negative duration and an invalid calendar date, then listed tasks
  to verify that neither invalid task had been saved.

## Implementation reference

Initial implementation commit: `2e73a863954d95b37aebebb1c92fe9515108b4c2`.
This records the AI-assisted implementation, not independent authorship of every
line.

## Team integration

Maintained the GitHub repository and coordinated the team review. Recorded
member details and the completed documentation, input-validation, and scheduling
reviews following the team's verbal discussion. Presentation preparation was
confirmed complete on October 13, 2026.

## Follow-up integration on October 12, 2026

At my request, the assistant reviewed and integrated five team commits through
`ca15673`: Sude's README feature summary (`779c6d0`), Abderraouf's CLI numeric
validation (`d9ddc12`), and Arian's username updates and planning tests
(`d147078`, `a1b6d06`, and `ca15673`).

I requested the follow-up corrections. The assistant fixed the indentation of
`test_exact_daily_capacity` and corrected Arian's GitHub profile URL targets in
the README and contribution record. The assistant then ran
`python3 -m unittest discover -s tests -v`; all 12 tests passed, and
`git diff --check` reported no whitespace errors.

I also requested updates to the README and individual contribution records to
reflect the actual commits while retaining the earlier verbal reviews. These
follow-up fixes and documentation updates are included together in this
integration commit. At that time, Arian's presentation preparation was pending.

## Follow-up integration on October 13, 2026

I confirmed that presentation preparation is complete and Arian is ready to
present. At my request, the assistant updated the README and contribution
records, clarified Arda's validation documentation after reviewing commit
`563ea45`, and corrected Arian's contribution filename and README link.
