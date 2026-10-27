import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from report import summarize, main


class ReportTests(unittest.TestCase):
    def fixture(self, text, directory):
        path = Path(directory)/'sales.csv'
        path.write_text(text, encoding='utf-8')
        return path

    def test_exact_money_and_aggregation(self):
        with tempfile.TemporaryDirectory() as directory:
            p = self.fixture('category,quantity,unit_price\nA,3,0.10\nA,1,0.20\n', directory)
            self.assertEqual(summarize(p), {'A':Decimal('0.50')})

    def test_bad_rows_fail_instead_of_silently_skipping(self):
        with tempfile.TemporaryDirectory() as directory:
            for row in ['A,1,NaN', 'A,0,1.00', 'A,1,1.001', ',1,1.00', 'A,1.5,2.00']:
                with self.subTest(row=row):
                    with self.assertRaises(ValueError):
                        summarize(self.fixture('category,quantity,unit_price\n'+row, directory))

    def test_formula_protection_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            p = self.fixture('category,quantity,unit_price\n=1+1,1,2.00\n', directory)
            output = Path(directory)/'out'
            main([str(p),'--output-dir',str(output)])
            self.assertIn("'=1+1",(output/'summary.csv').read_text(encoding='utf-8-sig'))
            with self.assertRaises(SystemExit):
                main([str(p),'--output-dir',str(output)])


if __name__ == '__main__':
    unittest.main()
