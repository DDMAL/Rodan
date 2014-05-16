# import unittest
# import tempfile
# import filecmp
# import shutil
# from rodan.jobs.util import taskutil
# from rodan.models import *
# from django.contrib.auth.models import User
# from rodan.helpers.exceptions import ObjectDeletedError
# from django.core.files import File


# class UUIDRegexTest(unittest.TestCase):

#     def test_get_uuid_from_url(self):
#         success_urls = ["http://idontcare.org/12345678901234567890123456abcdef",
#                         "http://idontcare.org/12345678901234567890123456abcdef/",
#                         "http://idontcare.org/1abc2319bc11234567890123deadbeef/blah/blah/12345678901234567890123456abcdef",
#                         "http://idontcare.org/12345678901234567890123456abcdef/?cooloption=true",
#                         "relpath/12345678901234567890123456abcdef?cooloption=true",
#                         "relpath/12345678901234567890123456abcdef/",
#                         "//relpath/12345678901234567890123456abcdef",
#                         "/relpath/12345678901234567890123456abcdef",
#                         "12345678901234567890123456abcdef"]

#         uuid = '12345678901234567890123456abcdef'

#         for url in success_urls:
#             self.assertEqual(taskutil.get_uuid_from_url(url), uuid)


# class SaveInstanceTest(unittest.TestCase):

#     def setUp(self):
#         self.test_user = User.objects.create(username='test_user')
#         self.test_project = Project.objects.create(creator=self.test_user, name='test_project')
#         self.test_page = Page.objects.create(project=self.test_project)
#         self.test_workflow = Workflow.objects.create(name='test_workflow', project=self.test_project, creator=self.test_user)
#         self.test_job = Job.objects.create(job_name='test_job')
#         self.test_workflowjob = WorkflowJob.objects.create(workflow=self.test_workflow, job=self.test_job)
#         self.test_workflowrun = WorkflowRun.objects.create(workflow=self.test_workflow, creator=self.test_user)
#         self.test_runjob = RunJob.objects.create(workflow_run=self.test_workflowrun, workflow_job=self.test_workflowjob, page=self.test_page)
#         self.test_result = Result.objects.create(run_job=self.test_runjob)

#         self.tdir = tempfile.mkdtemp()

#     def tearDown(self):
#         db_objects = [self.test_user, self.test_project, self.test_page,
#                       self.test_workflow, self.test_job, self.test_workflowjob,
#                       self.test_workflowrun, self.test_runjob, self.test_result]

#         for obj in db_objects:
#             if obj.pk is not None:  # This is necessary as opposed of "if obj.pk" because test_user.pk == 0
#                 obj.delete()
#         shutil.rmtree(self.tdir)

#     def test_save_instance(self):
#         # Result is an example object. This should work for every single model.
#         new_result = Result(run_job=self.test_runjob)
#         taskutil.save_instance(new_result)

#         #Checking if the new object was created.
#         self.assertIsNot(new_result.pk, None)
#         self.assertTrue(Result.objects.filter(pk=new_result.pk).exists())

#         #Checking resave prevention of deleted database object.
#         result_copy = Result.objects.get(pk=new_result.pk)
#         new_result.delete()
#         with self.assertRaises(ObjectDeletedError):
#             taskutil.save_instance(result_copy)

#     def test_save_file_field(self):
#         tfilepath = tempfile.mkstemp(dir=self.tdir)[1]
#         with open(tfilepath, 'w') as f:
#             f.write("some junk")
#         with open(tfilepath, 'rb') as f:
#             taskutil.save_file_field(self.test_result.result, '', File(f))

#         result_copy = Result.objects.get(pk=self.test_result.pk)
#         result_path = result_copy.result.path
#         self.assertTrue(filecmp.cmp(tfilepath, result_path))
#         result_copy.delete()
#         with self.assertRaises(ObjectDeletedError):
#             taskutil.save_file_field(self.test_result.result, '', File(f))
