# Library Loan Management

A self-contained Python and SQLite command-line application for browsing a
library catalogue and managing loans of physical book copies.

## Features

- List books or search titles and authors.
- Borrow and return physical book copies.
- Reject unavailable copies, missing borrowers and repeated returns.
- Display a borrower's loan history.
- Use a numbered interactive menu from PyCharm or the command line.
- Create and seed the SQLite database automatically on first run.

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

## Repository layout

| Path | Purpose |
| --- | --- |
| `library_loans/cli.py` | CLI, validation and interactive menu |
| `library_loans/database.py` | SQLite creation, schema and seed data |
| `library_loans/service.py` | Catalogue and lending operations |
| `tests/` | Automated unit and lifecycle tests |
| `docs/academic/` | Original assignment material retained for provenance |
