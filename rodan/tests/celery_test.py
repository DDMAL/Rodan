import unittest
import time
from rodan.tasks import add

class TestCeleryStuff(unittest.TestCase):
    def test_whatever(self):
        r = add.delay(8, 8)
        time.sleep(10)
        self.assertEqual(r.result, 16)
