"""Opt-in MySQL checks using rolled-back fixture records in an initialized DB."""

from concurrent.futures import ThreadPoolExecutor
import os
from threading import Barrier
import unittest
import uuid

import mysql.connector

from library_loans import service


@unittest.skipUnless(os.getenv("RUN_MYSQL_TESTS") == "1", "Set RUN_MYSQL_TESTS=1 for MySQL tests")
class MySQLTests(unittest.TestCase):
    def connect(self):
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"), port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "library_app"), password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "library_loans"), autocommit=False,
        )

    def setUp(self):
        self.conn = self.connect()
        self.addCleanup(self.conn.close)
        self.addCleanup(self.conn.rollback)
        self.isbn = uuid.uuid4().hex[:13]
        with self.conn.cursor() as cur:
            cur.execute("INSERT INTO bok VALUES (%s, 'Test book', 'Test author', 'Test', 2025, 100)",
                        (self.isbn,))
            cur.execute("INSERT INTO eksemplar VALUES (%s, 1)", (self.isbn,))
            cur.execute("INSERT INTO låner (Fornavn, Etternavn, Adresse) VALUES ('Test', 'Borrower', 'Fixture')")
            self.borrower = cur.lastrowid

    def test_lending_lifecycle(self):
        loan_id = service.borrow_book(self.conn, self.borrower, self.isbn, 1)
        with self.assertRaises(service.LoanError):
            service.borrow_book(self.conn, self.borrower, self.isbn, 1)
        self.assertEqual(service.loan_history(self.conn, self.borrower)[0][4], "On loan")
        service.return_book(self.conn, loan_id)
        with self.assertRaises(service.LoanError):
            service.return_book(self.conn, loan_id)
        self.assertEqual(service.loan_history(self.conn, self.borrower)[0][4], "Returned")
        service.borrow_book(self.conn, self.borrower, self.isbn, 1)

    def test_two_connections_cannot_lend_the_same_copy(self):
        self.conn.commit()
        ready = Barrier(2)
        try:
            def borrow():
                conn = self.connect()
                try:
                    ready.wait(timeout=10)
                    service.borrow_book(conn, self.borrower, self.isbn, 1)
                    conn.commit()
                    return "created"
                except service.LoanError:
                    conn.rollback()
                    return "rejected"
                finally:
                    conn.close()

            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(lambda _: borrow(), range(2)))
            self.assertCountEqual(results, ["created", "rejected"])
        finally:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM utlån WHERE ISBN = %s", (self.isbn,))
                cur.execute("DELETE FROM eksemplar WHERE ISBN = %s", (self.isbn,))
                cur.execute("DELETE FROM bok WHERE ISBN = %s", (self.isbn,))
                cur.execute("DELETE FROM låner WHERE LNr = %s", (self.borrower,))
            self.conn.commit()
