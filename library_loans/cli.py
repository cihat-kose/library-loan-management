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
    parser = argparse.ArgumentParser(description="Library Loan Management (MySQL)")

    def database_options(target, suppress=False):
        for name, default in (("host", "127.0.0.1"), ("port", "3306"),
                              ("user", "library_app"), ("password", "library-app-local"),
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
                            ("history", "Show a borrower's loan history"),
                            ("interactive", "Open the numbered interactive menu")):
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


def _prompt_positive_integer(prompt, input_fn=input, output_fn=print):
    while True:
        try:
            return positive_integer(input_fn(prompt))
        except argparse.ArgumentTypeError as exc:
            output_fn(f"Invalid input: {exc}")


def _prompt_date(prompt, input_fn=input, output_fn=print):
    while True:
        value = input_fn(prompt).strip()
        if not value:
            return None
        try:
            return iso_date(value)
        except argparse.ArgumentTypeError as exc:
            output_fn(f"Invalid input: {exc}")


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
    elif args.command == "interactive":
        return interactive(conn)
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


def interactive(conn, input_fn=input, output_fn=print):
    """Run the numbered menu while reusing the existing service operations."""
    while True:
        output_fn("\nLibrary Loan Management")
        output_fn("1. List books")
        output_fn("2. Search books")
        output_fn("3. Borrow a book")
        output_fn("4. Return a loan")
        output_fn("5. Loan history")
        output_fn("6. Exit")
        choice = input_fn("Choose an option: ").strip()

        try:
            if choice == "1":
                print_table(
                    ["ISBN", "Title", "Author", "Publisher", "Year", "Pages"],
                    service.list_books(conn),
                )
            elif choice == "2":
                text = input_fn("Search text: ").strip()
                print_table(
                    ["ISBN", "Title", "Author", "Publisher", "Year", "Pages"],
                    service.search_books(conn, text),
                )
            elif choice == "3":
                borrower = _prompt_positive_integer(
                    "Borrower ID: ", input_fn, output_fn
                )
                isbn = input_fn("ISBN: ").strip()
                copy_number = _prompt_positive_integer(
                    "Copy number: ", input_fn, output_fn
                )
                loan_date = _prompt_date(
                    "Loan date (YYYY-MM-DD, blank for today): ", input_fn, output_fn
                )
                loan_id = service.borrow_book(
                    conn, borrower, isbn, copy_number, loan_date
                )
                output_fn(f"Loan created: {loan_id}")
            elif choice == "4":
                loan_id = _prompt_positive_integer("Loan ID: ", input_fn, output_fn)
                service.return_book(conn, loan_id)
                output_fn(f"Loan {loan_id} returned.")
            elif choice == "5":
                borrower = _prompt_positive_integer(
                    "Borrower ID: ", input_fn, output_fn
                )
                print_table(
                    ["Loan", "Title", "Author", "Date", "Status"],
                    service.loan_history(conn, borrower),
                )
            elif choice == "6":
                output_fn("Goodbye.")
                return 0
            else:
                output_fn("Invalid option. Choose a number from 1 to 6.")
                continue
            conn.commit()
        except (mysql.connector.Error, service.LoanError) as exc:
            conn.rollback()
            output_fn(f"Error: {exc}")
