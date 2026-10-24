import unittest
import read_delivery_v7  # Configure the portable file-only package path.
from v7_validation import physical_photo_counts


class PhysicalCountTests(unittest.TestCase):
    def test_pending_review_does_not_zero_inventory(self):
        rows = [{'role': 'Mekân', 'sha256': str(i), 'completion_credit': False} for i in range(3)]
        self.assertEqual(physical_photo_counts(rows), {'photos': 3, 'hero_photos': 0})

    def test_shared_hash_or_source_is_one_frame_per_role(self):
        source = 'https://commons.wikimedia.org/wiki/File:Example.jpg'
        rows = [{'role': 'Mekân', 'sha256': 'first', 'source_url': source},
                {'role': 'Mekân', 'sha256': 'derivative', 'source_url': source},
                {'role': 'Mekân', 'sha256': 'first'},
                {'role': 'Kapak', 'sha256': 'first'}]
        self.assertEqual(physical_photo_counts(rows), {'photos': 1, 'hero_photos': 1})


if __name__ == '__main__':
    unittest.main()
