import contextlib
from datetime import date
import io
import os
import unittest
from unittest.mock import MagicMock, patch

import mysql.connector

from library_loans import cli, service


class ParserTests(unittest.TestCase):
    def test_options_on_either_side_keep_selected_command(self):
        for argv in (["--host", "db", "search", "--text", "Ibsen"],
                     ["search", "--text", "Ibsen", "--host", "db"]):
            args = cli.build_parser().parse_args(argv)
            self.assertEqual((args.host, args.command, args.text), ("db", "search", "Ibsen"))

    def test_invalid_inputs_fail_before_connecting(self):
        for argv in (["--unknown"], ["history", "--borrower", "0"],
                     ["borrow", "--borrower", "1", "--isbn", "x", "--copy", "1",
                      "--date", "2025-02-30"]):
            with self.subTest(argv=argv), patch.object(cli.mysql.connector, "connect") as connect:
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    cli.main(argv)
                connect.assert_not_called()

    def test_environment_port_is_validated(self):
        with patch.dict(os.environ, {"DB_PORT": "invalid"}):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                cli.build_parser().parse_args([])


class TransactionTests(unittest.TestCase):
    @patch.object(cli.mysql.connector, "connect")
    def test_default_lists_and_closes(self, connect):
        conn = connect.return_value
        conn.cursor.return_value.fetchall.return_value = []
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(cli.main([]), 0)
        self.assertIn("No records found", output.getvalue())
        conn.commit.assert_called_once()
        conn.close.assert_called_once()
        conn.cursor.return_value.close.assert_called_once()

    @patch.object(cli.mysql.connector, "connect")
    def test_database_failure_rolls_back_and_closes(self, connect):
        conn = connect.return_value
        conn.cursor.return_value.execute.side_effect = mysql.connector.Error("query failed")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main([]), 1)
        conn.rollback.assert_called_once()
        conn.commit.assert_not_called()
        conn.close.assert_called_once()
        conn.cursor.return_value.close.assert_called_once()

    @patch.object(cli.mysql.connector, "connect")
    def test_rejected_loan_rolls_back(self, connect):
        conn = connect.return_value
        conn.cursor.return_value.fetchone.return_value = None
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(["borrow", "--borrower", "99", "--isbn", "x",
                                       "--copy", "1"]), 1)
        conn.rollback.assert_called_once()
        conn.commit.assert_not_called()
        conn.close.assert_called_once()


class LendingTests(unittest.TestCase):
    def test_borrow_rejects_missing_borrower_missing_copy_and_active_loan(self):
        for rows in ([None], [(1,), None], [(1,), (1,), (42,)]):
            with self.subTest(rows=rows):
                conn = MagicMock()
                cursor = conn.cursor.return_value
                cursor.fetchone.side_effect = rows
                with self.assertRaises(service.LoanError):
                    service.borrow_book(conn, 3, "9000000000001", 1)
                self.assertFalse(any("INSERT" in call.args[0] for call in cursor.execute.call_args_list))
                cursor.close.assert_called_once()

    def test_borrow_inserts_bound_values(self):
        conn = MagicMock()
        cursor = conn.cursor.return_value
        cursor.fetchone.side_effect = [(1,), (1,), None]
        cursor.lastrowid = 7
        day = date(2025, 10, 29)
        self.assertEqual(service.borrow_book(conn, 3, "9000000000001", 1, day), 7)
        self.assertEqual(cursor.execute.call_args.args[1], ("9000000000001", 1, 3, day))
        cursor.close.assert_called_once()

    def test_return_rejects_missing_or_returned_loan(self):
        for row in (None, (1,)):
            conn = MagicMock()
            conn.cursor.return_value.fetchone.return_value = row
            with self.assertRaises(service.LoanError):
                service.return_book(conn, 5)
            self.assertEqual(conn.cursor.return_value.execute.call_count, 1)

    def test_return_updates_active_loan(self):
        conn = MagicMock()
        conn.cursor.return_value.fetchone.return_value = (0,)
        service.return_book(conn, 5)
        self.assertEqual(conn.cursor.return_value.execute.call_args.args[1], (5,))

    def test_search_keeps_sql_input_as_data(self):
        conn = MagicMock()
        text = "' OR 1=1 --"
        service.search_books(conn, text)
        sql, values = conn.cursor.return_value.execute.call_args.args
        self.assertNotIn(text, sql)
        self.assertEqual(values, (f"%{text}%", f"%{text}%"))


if __name__ == "__main__":
    unittest.main()
