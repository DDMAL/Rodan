import os
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status

from rodan.models.page import Page
from rodan.models.project import Project

# Refer to http://www.django-rest-framework.org/api-guide/testing


class PageViewTestCase(APITestCase):
    fixtures = ["1_users", "2_initial_data"]

    def setUp(self):
        self.media_root = os.path.join(settings.PROJECT_DIR)
        self.project_dir = os.path.join(self.media_root, "projects/9e8e928b4ec24a09b6113f1b0af1ea53/pages/2f63f986449349769d7a313e0fc6edb3/")

        # we need to fix the file paths on our Page object
        page = Page.objects.get(uuid="2f63f986449349769d7a313e0fc6edb3")
        page.page_image = SimpleUploadedFile('original_file.png', 'n/t')
        page.compat_page_image = SimpleUploadedFile('compat_page_image.png', 'n/t')
        page.save()

        self.client.login(username="ahankins", password="hahaha")

    def test_get_list(self):
        response = self.client.get("/pages/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_detail(self):
        response = self.client.get("/page/2f63f986449349769d7a313e0fc6edb3/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_no_files(self):
        page_obj = {
            'project': "http://localhost:8000/project/9e8e928b4ec24a09b6113f1b0af1ea53/",
            'page_order': 2
        }
        response = self.client.post("/pages/", page_obj, format="json")
        anticipated_message = {'message': 'You must supply at least one file to upload'}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_post_no_page_order(self):
        page_obj = {
            'project': "http://localhost:8000/project/9e8e928b4ec24a09b6113f1b0af1ea53/",
            'files': [
                SimpleUploadedFile('page1.png', 'n/t'),
                SimpleUploadedFile('page2.png', 'n/t')
            ]
        }
        response = self.client.post("/pages/", page_obj, format="multipart")
        anticipated_message = {'message': 'The start sequence for the page ordering may not be empty.'}
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_post_no_project(self):
        page_obj = {
            'page_order': 2,
            'files': [
                SimpleUploadedFile('page1.png', 'n/t'),
                SimpleUploadedFile('page2.png', 'n/t')
            ]
        }
        response = self.client.post("/pages/", page_obj, format="multipart")
        anticipated_message = {'message': 'You must supply a project identifier for the pages.'}

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, anticipated_message)

    def test_post(self):
        page_obj = {
            'project': "http://localhost:8000/project/9e8e928b4ec24a09b6113f1b0af1ea53/",
            'page_order': 2,
            'files': [
                SimpleUploadedFile('page1.png', 'n/t'),
                SimpleUploadedFile('page2.png', 'n/t')
            ]
        }
        response = self.client.post("/pages/", page_obj, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['pages']), 2)

        # check that the files are being saved in the proper place
        ## remember to lstrip the page path. Otherwise join will consider it
        # an absolute path and throw away the first bit.
        for page in response.data['pages']:
            fpath = os.path.join(self.media_root, page['page_image'].lstrip("/"))
            self.assertTrue(os.path.exists(fpath))

    def test_put(self):
        pass

    def test_patch(self):
        page_obj = {
            'name': 'New File Name'
        }
        response = self.client.patch("/page/2f63f986449349769d7a313e0fc6edb3/", page_obj, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check what we got back was what we sent out.
        self.assertEqual(response.data['name'], page_obj['name'])

    def test_delete(self):
        response = self.client.delete("/page/2f63f986449349769d7a313e0fc6edb3/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Page.objects.filter(uuid="2f63f986449349769d7a313e0fc6edb3").exists())

    def tearDown(self):
        # deleting the project will also delete the pages
        Project.objects.all().delete()
