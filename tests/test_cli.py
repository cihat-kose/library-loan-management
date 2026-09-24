import contextlib
import io
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from library_loans import cli, database, service


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = self.temp_dir.name + "\\test.db"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parser_rejects_invalid_values_before_connecting(self):
        with patch.object(cli.database, "connect") as connect:
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                cli.main(["borrow", "--borrower", "0", "--isbn", "x", "--copy", "1"])
            connect.assert_not_called()

    def test_database_is_created_and_seeded(self):
        conn = database.connect(self.path)
        self.assertEqual(service.search_books(conn, "Ibsen")[0][1], "Et dukkehjem")
        conn.close()

    def test_cli_lists_and_closes_database(self):
        with patch.dict("os.environ", {"DB_PATH": self.path}):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(cli.main([]), 0)
        self.assertIn("Et dukkehjem", output.getvalue())

    def test_cli_uses_requested_database_path(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["--database", self.path, "search", "--text", "Ibsen"]), 0)

    def test_lending_rules_and_rollback(self):
        conn = database.connect(self.path)
        with self.assertRaises(service.LoanError):
            service.borrow_book(conn, 999, "9000000000001", 1)
        loan_id = service.borrow_book(conn, 3, "9000000000001", 1)
        with self.assertRaises(service.LoanError):
            service.borrow_book(conn, 3, "9000000000001", 1)
        service.return_book(conn, loan_id)
        with self.assertRaises(service.LoanError):
            service.return_book(conn, loan_id)
        conn.close()

    def test_search_keeps_sql_input_as_data(self):
        conn = database.connect(self.path)
        text = "' OR 1=1 --"
        self.assertEqual(service.search_books(conn, text), [])
        conn.close()


if __name__ == "__main__":
    unittest.main()
