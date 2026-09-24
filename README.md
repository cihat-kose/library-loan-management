# Library Loan Management

A small Python and MySQL command-line application for browsing a library catalogue and managing loans of physical book copies. It is presented as the **Library Loan Management** project, with explicit validation, transaction handling and automated checks.

## Features

- List books or search titles and authors.
- Borrow an existing copy for an existing borrower.
- Reject loans for unavailable copies, and reject missing or repeated returns.
- Display a borrower's loan history.
- Use a numbered interactive menu from PyCharm or the command line.
- Use parameterized SQL and close connections after each command.

This is a local demonstration, without authentication, a web interface, borrower management or due-date tracking. Search uses MySQL `LIKE`: `%` and `_` retain their wildcard meaning.

## Requirements

- Python 3.10 or newer (locally verified with Python 3.13).
- MySQL 8.4; Docker with the Compose plugin is the provided setup route.
- Internet access for the initial Python package and container downloads.

## Install

Run these commands from the repository root. Creating the virtual environment and installing the package works in PowerShell, macOS and Linux; select the appropriate activation command.

```text
python -m venv .venv
```

PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```sh
source .venv/bin/activate
```

Then:

```text
python -m pip install -r requirements.txt
python -m library_loans --help
```

If PowerShell blocks activation, use `.venv\Scripts\python` in place of `python`. The installed `library-loans` command is equivalent to `python -m library_loans`.

## Start the demo database

Copy `.env.example` to `.env` (`Copy-Item .env.example .env` in PowerShell or `cp .env.example .env` in a POSIX shell). Replace both placeholder passwords with local demo credentials, then run:

```text
docker compose up -d --wait
```

Compose creates the schema and demonstration data on the first start with an empty volume. It binds MySQL to localhost on port 3306. If that port is occupied, change the host port in `compose.yaml` and set `DB_PORT` accordingly.

The Python CLI reads environment variables, **not** the `.env` file. Set `DB_PASSWORD` in your terminal to the same value used in `.env`:

```powershell
$env:DB_PASSWORD = 'your-local-demo-password'
```

Or in a POSIX shell:

```sh
export DB_PASSWORD='your-local-demo-password'
```

| Variable | Default |
| --- | --- |
| `DB_HOST` | `127.0.0.1` |
| `DB_PORT` | `3306` |
| `DB_USER` | `library_app` |
| `DB_PASSWORD` | Empty; configure before connecting |
| `DB_NAME` | `library_loans` |

Connection options (`--host`, `--port`, `--user`, `--password`, `--database`) can appear before or after a subcommand. Prefer the environment for passwords to keep them out of command arguments.

For an existing MySQL server, create an empty UTF-8 database and a user with access to it. In a MySQL client session connected to that database, run `SOURCE sql/schema.sql;` and then `SOURCE sql/seed.sql;` from the repository root. These are one-time initialization scripts, not migrations; they do not drop an existing database. Configure the variables above for your server. Norwegian table and column names are retained from the original data model.

Stop the demo with `docker compose down`. The named volume keeps data. Schema or seed changes are not reapplied to an existing volume.

## Usage

```text
python -m library_loans
python -m library_loans search --text Ibsen
python -m library_loans borrow --isbn 9000000000001 --copy 1 --borrower 3
python -m library_loans history --borrower 3
```

With fresh seed data, the search matches *Et dukkehjem* by Henrik Ibsen. Borrowing prints the new loan ID. Use that ID to return the loan, for example:

```text
python -m library_loans return --loan 2
```

The example ID is only valid if that loan exists. Borrow optionally accepts `--date 2025-10-29`; otherwise it uses today's date on the client machine. Commands return status `0` on success, `1` for database or lending errors, and `2` for invalid arguments. Omitting a subcommand lists the catalogue.

## Run from PyCharm

The shared **Library Loan Management (interactive)** Run Configuration starts
`python -m library_loans interactive` with the project directory as its working
directory. Select it in the configuration dropdown and press the green Run
button to open the numbered menu.

Before the first run, start MySQL with `docker compose up -d --wait` as
described above. In PyCharm, open **Run | Edit Configurations**, select the
shared configuration, and add `DB_PASSWORD` under **Environment variables**
using the same local password as `.env`. Keep the value in PyCharm's local
configuration and do not add it to the shared XML or source control. Add
`DB_HOST`, `DB_PORT`, `DB_USER`, or `DB_NAME` there only when your local
database differs from the defaults.

## Tests and quality focus

No database is needed for the default test command:

```text
python -m unittest discover -s tests -v
python -m pip check
```

Unit tests cover argument routing, invalid input, parameter binding, lending rules, rollback and resource cleanup. They use mocked database connections and do not establish SQL correctness on their own.

To run the MySQL integration tests, start the demo database, configure `DB_PASSWORD`, and enable them:

```powershell
$env:RUN_MYSQL_TESTS = '1'
python -m unittest discover -s tests -v
```

POSIX equivalent:

```sh
RUN_MYSQL_TESTS=1 python -m unittest discover -s tests -v
```

Integration tests exercise the lending lifecycle and competing connections. They use unique fixture records, rolling them back or deleting them afterwards; the concurrency test commits temporary fixtures. Use a disposable demo database. Row locks serialize borrowing through this application; direct SQL writers must follow the same locking protocol.

GitHub Actions is configured for unit tests on Python 3.10 and 3.13, plus integration tests against MySQL 8.4. No hosted CI result is claimed until the workflow actually runs.

Local verification: package installation, both help entry points, dependency consistency and 15 unit tests passed on Python 3.13.15. The two integration tests were skipped because no MySQL/Docker runtime was available. The container startup, SQL initialization and database-backed usage examples still require that environment for end-to-end verification.

## Repository layout

| Path | Purpose |
| --- | --- |
| `library_loans/cli.py` | English CLI, validation and transaction lifetime |
| `library_loans/service.py` | Catalogue and lending operations |
| `sql/schema.sql` | Tables, keys, constraints and indexes |
| `sql/seed.sql` | Demonstration catalogue and fictional borrower records |
| `sql/queries.sql` | SQL examples, including data-changing statements; use on demo data |
| `tests/` | Unit tests and opt-in MySQL integration tests |
| `compose.yaml` | Local MySQL service with persistent data |
| `docs/schema.png` | Original database diagram |
| `docs/academic/` | Assignment PDF and original README retained for provenance |

The original README is a historical document; its feature and test claims are not the current verification record. Some catalogue ISBNs and book metadata are illustrative rather than bibliographic reference data.

## Changes from the assignment version

The entry point changed from `oppgave4.py` to `python -m library_loans`. Commands are now `list`, `search`, `borrow`, `return`, `history` and `interactive`, with English option names. The default database is now `library_loans`; use `DB_NAME=ga_bibliotek` for an existing original database. No existing database is migrated automatically.

The hard-coded password was removed. Invalid operations now return a failure status, unknown arguments are rejected, database flags no longer bypass the requested command, and each invocation closes its connection. Loans use locking reads to prevent concurrent borrowing through the CLI. The default loan date now comes from the client clock instead of the database clock. The SQL example for never-borrowed books now checks all copies correctly.
