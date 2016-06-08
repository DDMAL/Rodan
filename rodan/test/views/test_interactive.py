import uuid, json
from rest_framework.test import APITestCase
from rest_framework import status
from model_mommy import mommy
from rodan.test.helpers import RodanTestSetUpMixin, RodanTestTearDownMixin
from rodan.models import Resource, Job, ResourceType, RunJob
from rodan.constants import task_status
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
import datetime
from django.utils import timezone

class InteractiveAcquireTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def _acquire(self):
        return self.client.post(reverse('interactive-acquire', kwargs={'run_job_uuid': self.test_runjob.pk}))

    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()
        self.client.force_authenticate(user=self.test_superuser)
        self.test_runjob = mommy.make('rodan.RunJob',
                                      status=task_status.WAITING_FOR_INPUT)
    def test_not_interactive(self):
        self.test_runjob.status = task_status.FINISHED
        self.test_runjob.save()
        response = self._acquire()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'This RunJob does not accept input now')

    def test_success_first_working_user(self):
        response = self._acquire()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        test_rj = RunJob.objects.get(uuid=self.test_runjob.uuid)  # refetch
        self.assertEqual(test_rj.working_user, self.test_superuser)
        self.assertEqual(response.data['working_url'], "http://testserver" + reverse('interactive-working', kwargs={'run_job_uuid': self.test_runjob.pk, 'working_user_token': str(test_rj.working_user_token), 'additional_url': ''}))

    def test_success_continue_working_same_token(self):
        self.test_runjob.working_user = self.test_superuser
        self.test_runjob.working_user_token = uuid.uuid4()
        t = self.test_runjob.working_user_token
        self.test_runjob.working_user_expiry = timezone.now() + datetime.timedelta(seconds=1)
        self.test_runjob.save()
        response = self._acquire()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        test_rj = RunJob.objects.get(uuid=self.test_runjob.uuid)  # refetch
        self.assertEqual(test_rj.working_user, self.test_superuser)
        self.assertEqual(test_rj.working_user_token, t)

    def test_success_self_expired_change_token(self):
        self.test_runjob.working_user = self.test_superuser
        self.test_runjob.working_user_token = uuid.uuid4()
        t = self.test_runjob.working_user_token
        self.test_runjob.working_user_expiry = timezone.now() + datetime.timedelta(seconds=-1)
        self.test_runjob.save()
        response = self._acquire()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        test_rj = RunJob.objects.get(uuid=self.test_runjob.uuid)  # refetch
        self.assertEqual(test_rj.working_user, self.test_superuser)
        self.assertNotEqual(test_rj.working_user_token, t)

    def test_success_others_have_expired(self):
        self.test_runjob.working_user = self.test_user
        self.test_runjob.working_user_expiry = timezone.now() + datetime.timedelta(seconds=-0.1)
        self.test_runjob.save()
        response = self._acquire()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        test_rj = RunJob.objects.get(uuid=self.test_runjob.uuid)  # refetch
        self.assertEqual(test_rj.working_user, self.test_superuser)

    def test_fail_others_working(self):
        self.test_runjob.working_user = self.test_user
        self.test_runjob.working_user_expiry = timezone.now() + datetime.timedelta(seconds=+10)
        self.test_runjob.save()
        response = self._acquire()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Previous working user has not expired yet.')


class InteractiveWorkingTestCase(RodanTestTearDownMixin, APITestCase, RodanTestSetUpMixin):
    def setUp(self):
        self.setUp_rodan()
        self.setUp_user()

        from rodan.test.dummy_jobs import dummy_manual_job
        dummy_m_job = Job.objects.get(name=dummy_manual_job.name)
        self.test_project = mommy.make('rodan.Project')
        self.test_workflow = mommy.make('rodan.Workflow', project=self.test_project)
        self.test_resource_in = mommy.make('rodan.Resource',
                                           project=self.test_project,
                                           resource_file="dummy",
                                           resource_type=ResourceType.objects.get(mimetype='test/a1'))
        self.test_resource_out = mommy.make('rodan.Resource',
                                            project=self.test_project,
                                            resource_file="",
                                            resource_type=ResourceType.objects.get(mimetype='test/a1'))
        self.test_working_user_token = uuid.uuid4()
        self.test_runjob = mommy.make('rodan.RunJob',
                                      job_name=dummy_m_job.name,
                                      status=task_status.WAITING_FOR_INPUT,
                                      working_user=self.test_user,
                                      working_user_token=self.test_working_user_token,
                                      working_user_expiry=timezone.now() + datetime.timedelta(seconds=+10),
                                      workflow_run__status=task_status.PROCESSING,
                                      workflow_run__workflow=self.test_workflow)
        input_m = mommy.make('rodan.Input',
                             run_job=self.test_runjob,
                             input_port_type_name='in_typeA',
                             resource=self.test_resource_in)
        output_m = mommy.make('rodan.Output',
                              run_job=self.test_runjob,
                              output_port_type_name='out_typeA',
                              resource=self.test_resource_out)
        self.test_resource_out.origin = output_m
        self.test_resource_out.save()
        self.test_resource_in.resource_file.save('dummy.txt', ContentFile('{"test": "hahaha"}'))

    def test_not_exist(self):
        response = self.client.get(reverse('interactive-working', kwargs={'run_job_uuid': uuid.uuid1(), 'working_user_token': uuid.uuid1(), 'additional_url': ''}), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.post(reverse('interactive-working', kwargs={'run_job_uuid': uuid.uuid1(), 'working_user_token': uuid.uuid1(), 'additional_url': ''}), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_not_waiting_for_input(self):
        self.test_runjob.status = task_status.SCHEDULED
        self.test_runjob.save()
        response = self.client.get(reverse('interactive-working', kwargs={'run_job_uuid': self.test_runjob.uuid, 'working_user_token': uuid.uuid1(), 'additional_url': ''}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'message': 'This RunJob does not accept input now'})
        response = self.client.post(reverse('interactive-working', kwargs={'run_job_uuid': self.test_runjob.uuid, 'working_user_token': uuid.uuid1(), 'additional_url': ''}), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'message': 'This RunJob does not accept input now'})

    def test_wrong_token(self):
        response = self.client.get(reverse('interactive-working', kwargs={'run_job_uuid': self.test_runjob.uuid, 'working_user_token': uuid.uuid1(), 'additional_url': ''}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'message': 'Permission denied'})
        response = self.client.post(reverse('interactive-working', kwargs={'run_job_uuid': self.test_runjob.uuid, 'working_user_token': uuid.uuid1(), 'additional_url': ''}), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'message': 'Permission denied'})

    def test_expired(self):
        self.test_runjob.working_user_expiry = timezone.now() + datetime.timedelta(seconds=-1)
        self.test_runjob.save()
        response = self.client.get(reverse('interactive-working', kwargs={'run_job_uuid': self.test_runjob.uuid, 'working_user_token': self.test_working_user_token, 'additional_url': ''}))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'message': 'Permission denied'})
        response = self.client.post(reverse('interactive-working', kwargs={'run_job_uuid': self.test_runjob.uuid, 'working_user_token': self.test_working_user_token, 'additional_url': ''}), format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {'message': 'Permission denied'})

    def test_get__success(self):
        response = self.client.get(reverse('interactive-working', kwargs={'run_job_uuid': self.test_runjob.uuid, 'working_user_token': self.test_working_user_token, 'additional_url': ''}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, "dummy hahaha")

    def test_post__fail(self):
        response = self.client.post(reverse('interactive-working', kwargs={'run_job_uuid': self.test_runjob.uuid, 'working_user_token': self.test_working_user_token, 'additional_url': ''}), {'fail': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'detail': 'dummy manual job error'})

    def test_post__success(self):
        response = self.client.post(reverse('interactive-working', kwargs={'run_job_uuid': self.test_runjob.uuid, 'working_user_token': self.test_working_user_token, 'additional_url': ''}), [1,2,3,4], format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        path = Resource.objects.get(uuid=self.test_resource_out.uuid).resource_file.path
        with open(path) as f:
            self.assertEqual(json.load(f), [1, 2, 3, 4])
