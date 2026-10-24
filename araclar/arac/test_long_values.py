"""Regression checks for the lossless Excel long-value archive decoder."""
import hashlib
import json
import unittest
from read_delivery_v7 import archive_values, restore


class Sheet:
    def __init__(self, rows):
        self.rows = rows

    def iter_rows(self, **kwargs):
        return iter(self.rows)


class Workbook(dict):
    @property
    def sheetnames(self):
        return list(self)


class LongValueTests(unittest.TestCase):
    def setUp(self):
        self.value = json.dumps({'a': 'çığ' * 15000}, ensure_ascii=False)
        self.sha = hashlib.sha256(self.value.encode()).hexdigest()
        self.key = 'long-fixture'
        self.meta = [self.key, 'evidence', 'evidence:1', 'source_evidence_json', self.sha]
        self.rows = [self.meta + [i, self.value[n:n+12000]] for i, n in enumerate(range(0, len(self.value), 12000))]
        self.marker = {'corteqs_long_value': self.key, 'sha256': self.sha}

    def test_chunks_restore_exact_unicode_object(self):
        archive = archive_values(Workbook(UzunAlanlar=Sheet(self.rows[::-1])))
        self.assertEqual(restore(self.marker, archive, 'evidence', 'evidence:1', 'source_evidence_json'), json.loads(self.value))

    def test_missing_or_duplicate_chunk_fails(self):
        for rows in (self.rows[1:], self.rows + [self.rows[0]]):
            with self.assertRaises(ValueError):
                archive_values(Workbook(UzunAlanlar=Sheet(rows)))

    def test_altered_bytes_fail(self):
        rows = [r[:] for r in self.rows]
        rows[0][-1] += 'changed'
        with self.assertRaises(ValueError):
            archive_values(Workbook(UzunAlanlar=Sheet(rows)))

    def test_reference_cannot_point_to_another_row(self):
        archive = archive_values(Workbook(UzunAlanlar=Sheet(self.rows)))
        with self.assertRaises(ValueError):
            restore(self.marker, archive, 'evidence', 'evidence:2', 'source_evidence_json')


if __name__ == '__main__':
    unittest.main()
