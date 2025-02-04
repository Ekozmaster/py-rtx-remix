from unittest import TestCase

from src.py_rtx_remix.api_data_types import HASH


class TestHASH(TestCase):
    def test_call_with_value(self):
        hash_value = HASH(0x4)
        self.assertEqual(hash_value.value, 0x4)

    def test_call_without_value(self):
        hash_value = HASH()
        self.assertGreater(hash_value.value, 0x0)
