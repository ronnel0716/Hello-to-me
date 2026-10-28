import tempfile
import unittest
from pathlib import Path
from check_inventory import audit, html_report, write_reports

HEADER = 'asset_tag,device_type,serial_number,assigned_to,location,status\n'


class InventoryTests(unittest.TestCase):
    def test_demo_counts_and_read_only(self):
        path = Path(__file__).with_name('sample.csv')
        before = path.read_bytes()
        result = audit(path)
        self.assertEqual([result[k] for k in ('total_records','flagged_records','clean_records','issue_count')], [8,4,4,6])
        self.assertEqual(path.read_bytes(), before)

    def test_identifiers_ignore_case_and_space(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'input.csv'
            path.write_text(HEADER+'A,Laptop,serial,One,Office,ACTIVE\n a ,Laptop,SERIAL,Two,Office,active\n')
            result = audit(path)
            self.assertEqual(result['flagged_records'], 2)
            self.assertEqual(result['issue_count'], 4)

    def test_bad_schema_empty_and_extra_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'input.csv'
            for text in ['tag,status\nA,active', HEADER, HEADER+'A,B,C,D,E,active,unexpected\n']:
                path.write_text(text)
                with self.assertRaises(ValueError):
                    audit(path)

    def test_escaping_csv_protection_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'input.csv'
            path.write_text(HEADER+'=1+1,<script>,S1,,Office,active\n')
            result = audit(path)
            page = html_report(result)
            self.assertNotIn('<script>', page)
            self.assertIn('&lt;script&gt;', page)
            out = Path(directory)/'out'
            write_reports(result,out)
            self.assertIn("'=1+1",(out/'findings.csv').read_text(encoding='utf-8-sig'))
            with self.assertRaises(ValueError):
                write_reports(result,out)


if __name__ == '__main__':
    unittest.main()
