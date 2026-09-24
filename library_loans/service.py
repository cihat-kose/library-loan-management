"""Parameterized SQLite operations. Callers own the connection and transaction."""

from contextlib import closing
from datetime import date


class LoanError(ValueError):
    """An operation conflicts with the current lending state."""


def list_books(conn):
    with closing(conn.cursor()) as cursor:
        cursor.execute(
            "SELECT ISBN, Tittel, Forfatter, Forlag, UtgittÅr, AntallSider "
            "FROM bok ORDER BY Tittel"
        )
        return cursor.fetchall()


def search_books(conn, text):
    with closing(conn.cursor()) as cursor:
        pattern = f"%{text}%"
        cursor.execute(
            "SELECT ISBN, Tittel, Forfatter, Forlag, UtgittÅr, AntallSider "
            "FROM bok WHERE Tittel LIKE ? OR Forfatter LIKE ? "
            "ORDER BY Forfatter, Tittel", (pattern, pattern)
        )
        return cursor.fetchall()


def borrow_book(conn, borrower_id, isbn, copy_number, loan_date=None):
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT 1 FROM låner WHERE LNr = ?", (borrower_id,))
        if cursor.fetchone() is None:
            raise LoanError(f"Borrower {borrower_id} does not exist.")
        cursor.execute(
            "SELECT 1 FROM eksemplar WHERE ISBN = ? AND EksNr = ?",
            (isbn, copy_number),
        )
        if cursor.fetchone() is None:
            raise LoanError("Book copy does not exist.")
        cursor.execute(
            "SELECT UtlånsNr FROM utlån WHERE ISBN = ? AND EksNr = ? "
            "AND Levert = 0", (isbn, copy_number)
        )
        if cursor.fetchone() is not None:
            raise LoanError("Book copy is already on loan.")
        cursor.execute(
            "INSERT INTO utlån (ISBN, EksNr, LNr, Utlånsdato, Levert) "
            "VALUES (?, ?, ?, ?, 0)",
            (isbn, copy_number, borrower_id, (loan_date or date.today()).isoformat()),
        )
        return cursor.lastrowid


def return_book(conn, loan_id):
    with closing(conn.cursor()) as cursor:
        cursor.execute(
            "SELECT Levert FROM utlån WHERE UtlånsNr = ?", (loan_id,)
        )
        row = cursor.fetchone()
        if row is None:
            raise LoanError(f"Loan {loan_id} does not exist.")
        if row[0] == 1:
            raise LoanError("Loan has already been returned.")
        cursor.execute("UPDATE utlån SET Levert = 1 WHERE UtlånsNr = ?", (loan_id,))


def loan_history(conn, borrower_id):
    with closing(conn.cursor()) as cursor:
        cursor.execute("SELECT 1 FROM låner WHERE LNr = ?", (borrower_id,))
        if cursor.fetchone() is None:
            raise LoanError(f"Borrower {borrower_id} does not exist.")
        cursor.execute(
            "SELECT u.UtlånsNr, b.Tittel, b.Forfatter, u.Utlånsdato, "
            "CASE WHEN u.Levert = 1 THEN 'Returned' ELSE 'On loan' END "
            "FROM utlån u JOIN bok b ON b.ISBN = u.ISBN "
            "WHERE u.LNr = ? ORDER BY u.Utlånsdato DESC, u.UtlånsNr DESC",
            (borrower_id,),
        )
        return cursor.fetchall()
