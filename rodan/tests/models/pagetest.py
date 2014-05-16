from django.test import TestCase
from rodan.models import *


class PageTestCase(TestCase):
	def test_save(self):
		self = Page.objects.create()
		self.save()
		self.assertEqual(self.page_path, os.path.join(self.project.project_path, "pages", str(self.uuid)))
		self.assertisNotNone(self.page_path)
		self.assertisNotNone(self.thumb_path)