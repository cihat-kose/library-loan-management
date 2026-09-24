# Library Loan Management

[![Tests](https://img.shields.io/github/actions/workflow/status/cihat-kose/library-loan-management/tests.yml?style=for-the-badge&label=CI%20Tests&logo=github)](https://github.com/cihat-kose/library-loan-management/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![CLI](https://img.shields.io/badge/Interface-CLI-222222?style=for-the-badge&logo=gnubash&logoColor=white)](https://docs.python.org/3/library/argparse.html)
[![Tests](https://img.shields.io/badge/Tests-unittest-6DB33F?style=for-the-badge&logo=testinglibrary&logoColor=white)](https://docs.python.org/3/library/unittest.html)
[![License](https://img.shields.io/badge/License-MIT-F7DF1E?style=for-the-badge&logo=open-source-initiative&logoColor=black)](LICENSE)

A self-contained Python and SQLite command-line application for browsing a
library catalogue and managing loans of physical book copies.

This project demonstrates a small, dependency-light Python application with
input validation, parameterized SQL, transaction handling, automated tests and
a database that initializes itself on first run.

## Features

- List books or search titles and authors.
- Borrow and return physical book copies.
- Reject unavailable copies, missing borrowers and repeated returns.
- Display a borrower's loan history.
- Use a numbered interactive menu from PyCharm or the command line.
- Create and seed the SQLite database automatically on first run.

## Technology stack

- **Python 3.10+** — application language and standard-library tooling.
- **SQLite** — local relational database with no server setup.
- **argparse** — command-line parsing and validation.
- **unittest** — automated unit and lifecycle tests.
- **GitHub Actions** — continuous testing on Python 3.10 and 3.13.

## Requirements

- Python 3.10 or newer.
- No Docker, MySQL server or external database is required.

## Install and run

From the repository root:

```text
python -m venv .venv
```

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m library_loans interactive
```

The first run creates `library_loans.db`, applies the schema and inserts the
fictional demonstration catalogue and borrowers. The database file is local
and is ignored by Git. Press **Run** in PyCharm using the shared
**Library Loan Management (interactive)** configuration to start the menu.

## Usage

```text
python -m library_loans
python -m library_loans search --text Ibsen
python -m library_loans borrow --isbn 9000000000001 --copy 1 --borrower 3
python -m library_loans history --borrower 3
python -m library_loans return --loan 2
```

Use `--database path\to\file.db` or the `DB_PATH` environment variable to
select another SQLite file. Omitting a subcommand lists the catalogue.
Commands return status `0` on success, `1` for database or lending errors,
and `2` for invalid arguments.

## Tests

```text
python -m unittest discover -s tests -v
python -m pip check
```

The tests use temporary SQLite files and do not require external services.

## Design notes

- SQL values are always passed as parameters rather than interpolated into
  queries.
- Each CLI invocation owns one transaction and closes its database connection.
- The database schema and fictional seed data are created idempotently, so a
  fresh checkout is immediately runnable.
- `library_loans.db` is local application data and is intentionally excluded
  from version control.

## Roadmap

- [ ] Add borrower management commands.
- [ ] Add due dates and overdue-loan reporting.
- [ ] Add CSV export for catalogue and loan history.
- [ ] Add a small web API on top of the service layer.

## Repository layout

| Path | Purpose |
| --- | --- |
| `library_loans/cli.py` | CLI, validation and interactive menu |
| `library_loans/database.py` | SQLite creation, schema and seed data |
| `library_loans/service.py` | Catalogue and lending operations |
| `tests/` | Automated unit and lifecycle tests |
| `docs/academic/` | Original assignment material retained for provenance |
