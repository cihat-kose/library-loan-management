import tempfile
import unittest

from library_loans import database, service


class SQLiteLifecycleTests(unittest.TestCase):
    def test_database_is_self_contained(self):
        with tempfile.TemporaryDirectory() as directory:
            conn = database.connect(directory + "\\library.db")
            loan_id = service.borrow_book(conn, 3, "9000000000001", 1)
            self.assertEqual(service.loan_history(conn, 3)[0][0], loan_id)
            service.return_book(conn, loan_id)
            self.assertEqual(service.loan_history(conn, 3)[0][4], "Returned")
            conn.close()


if __name__ == "__main__":
    unittest.main()
