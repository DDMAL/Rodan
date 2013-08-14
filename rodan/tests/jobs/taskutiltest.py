import unittest
from rodan.jobs.util import taskutil


class TaskutilTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_uuid_from_url(self):
        success_urls = ["http://idontcare.org/12345678901234567890123456abcdef",
                        "http://idontcare.org/12345678901234567890123456abcdef/",
                        "http://idontcare.org/1abc2319bc11234567890123deadbeef/blah/blah/12345678901234567890123456abcdef",
                        "http://idontcare.org/12345678901234567890123456abcdef/?cooloption=true",
                        "relpath/12345678901234567890123456abcdef?cooloption=true",
                        "relpath/12345678901234567890123456abcdef/",
                        "//relpath/12345678901234567890123456abcdef",
                        "/relpath/12345678901234567890123456abcdef",
                        "12345678901234567890123456abcdef"]

        uuid = '12345678901234567890123456abcdef'

        for url in success_urls:
            self.assertEqual(taskutil.get_uuid_from_url(url), uuid)
