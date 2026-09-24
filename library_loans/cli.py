"""Command parsing, connection lifetime and console output."""

import argparse
from datetime import date
import os
import sys

import mysql.connector

from library_loans import service


def positive_integer(value):
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Expected a positive integer.") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("Expected a positive integer.")
    return number


def iso_date(value):
    try:
        parsed = date.fromisoformat(value)
        if parsed.isoformat() != value:
            raise ValueError
        return parsed
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use a valid date in YYYY-MM-DD format.") from exc


def build_parser():
    parser = argparse.ArgumentParser(description="Library Loans CLI (MySQL)")

    def database_options(target, suppress=False):
        for name, default in (("host", "127.0.0.1"), ("port", "3306"),
                              ("user", "library_app"), ("password", ""),
                              ("database", "library_loans")):
            env_name = "DB_NAME" if name == "database" else f"DB_{name.upper()}"
            target.add_argument(
                f"--{name}", type=positive_integer if name == "port" else str,
                default=argparse.SUPPRESS if suppress else os.getenv(env_name, default),
                help=f"MySQL {name}; defaults to {env_name}",
            )

    database_options(parser)
    commands = parser.add_subparsers(dest="command")
    for name, help_text in (("list", "List all books (default)"),
                            ("search", "Search titles and authors"),
                            ("borrow", "Register a loan"),
                            ("return", "Return a loan"),
                            ("history", "Show a borrower's loan history")):
        sub = commands.add_parser(name, help=help_text)
        database_options(sub, suppress=True)
        if name == "search":
            sub.add_argument("--text", required=True)
        if name in ("borrow", "history"):
            sub.add_argument("--borrower", type=positive_integer, required=True)
        if name == "borrow":
            sub.add_argument("--isbn", required=True)
            sub.add_argument("--copy", type=positive_integer, required=True)
            sub.add_argument("--date", type=iso_date)
        if name == "return":
            sub.add_argument("--loan", type=positive_integer, required=True)
    return parser


def print_table(headers, rows):
    values = [["" if value is None else str(value) for value in row] for row in rows]
    widths = [max(len(header), *(len(row[i]) for row in values))
              if values else len(header) for i, header in enumerate(headers)]
    for row in [headers, ["-" * width for width in widths], *values]:
        print(" | ".join(value.ljust(width) for value, width in zip(row, widths)))
    if not values:
        print("No records found.")


def run(conn, args):
    if args.command in (None, "list", "search"):
        rows = (service.search_books(conn, args.text) if args.command == "search"
                else service.list_books(conn))
        print_table(["ISBN", "Title", "Author", "Publisher", "Year", "Pages"], rows)
    elif args.command == "borrow":
        loan_id = service.borrow_book(conn, args.borrower, args.isbn, args.copy, args.date)
        return f"Loan created: {loan_id}"
    elif args.command == "return":
        service.return_book(conn, args.loan)
        return f"Loan {args.loan} returned."
    else:
        print_table(["Loan", "Title", "Author", "Date", "Status"],
                    service.loan_history(conn, args.borrower))


def main(argv=None):
    args = build_parser().parse_args(argv)
    conn = None
    try:
        conn = mysql.connector.connect(
            host=args.host, port=args.port, user=args.user, password=args.password,
            database=args.database, connection_timeout=5, autocommit=False,
        )
        message = run(conn, args)
        conn.commit()
        if message:
            print(message)
        return 0
    except (mysql.connector.Error, service.LoanError) as exc:
        if conn is not None:
            conn.rollback()
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        if conn is not None:
            conn.close()
