import unittest
from functionalities import get_prices, sum_numbers, upload_via_pandas
from app import *
import sqlite3

class FuncCase(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.ticker = 'MSFT'

    def tearDown(self):
        self.conn.close()

    def test_upload_via_pandas(self):
        upload_via_pandas(self.ticker, self.conn)

        # Check that the table exists
        cursor = self.conn.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="hist_from_pandas"')
        self.assertEqual(cursor.fetchone()[0], 'hist_from_pandas')

        # Check that the table has the correct columns
        cursor.execute('PRAGMA table_info(hist_from_pandas)')
        columns = [row[1] for row in cursor.fetchall()]
        expected_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits', 'Ticker']
        self.assertEqual(columns, expected_columns)

        # Check that the table has data
        cursor.execute('SELECT COUNT(*) FROM hist_from_pandas')
        self.assertGreater(cursor.fetchone()[0], 0)

    def test_upload_via_pandas_empty_table(self):
        upload_via_pandas(self.ticker, self.conn)
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM hist_from_pandas')
        count = cursor.fetchone()[0]
        upload_via_pandas(self.ticker, self.conn)  # upload again to replace table
        cursor.execute('SELECT COUNT(*) FROM hist_from_pandas')
        self.assertEqual(cursor.fetchone()[0], count)

    def test_upload_via_pandas_invalid_ticker(self):
        with self.assertRaises(Exception):
            upload_via_pandas('INVALID_TCKR', self.conn)

    def test_upload_via_pandas_invalid_conn(self):
        with self.assertRaises(Exception):
            upload_via_pandas(self.ticker, None)

    def test_get_prices(self):
        df = get_prices(self.ticker)
        self.assertTrue(isinstance(df, list))



