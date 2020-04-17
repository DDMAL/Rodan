import os
import sys
import traceback
import getpass
import subprocess

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, User, Group
from django.db.models.signals import (
    pre_migrate,
    post_migrate,
    pre_save,
    pre_delete,
    post_save,
    post_delete
)
from django.dispatch import receiver
from django.conf import settings
from guardian.shortcuts import assign_perm
import psycopg2
import psycopg2.extensions

from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from rodan.models.inputport import InputPort
from rodan.models.outputport import OutputPort
from rodan.models.input import Input
from rodan.models.output import Output
from rodan.models.project import Project
from rodan.models.job import Job
from rodan.models.userpreference import UserPreference
from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflow import Workflow
from rodan.models.workflowjobgroup import WorkflowJobGroup
from rodan.models.workflowrun import WorkflowRun
from rodan.models.runjob import RunJob
from rodan.models.resultspackage import ResultsPackage
from rodan.models.resource import Resource
from rodan.models.resourcelabel import ResourceLabel
from rodan.models.resourcelist import ResourceList
from rodan.models.resourcetype import ResourceType
from rodan.models.connection import Connection
from rodan.models.tempauthtoken import Tempauthtoken
from rodan.models.workflowjobcoordinateset import WorkflowJobCoordinateSet
from rodan.models.workflowjobgroupcoordinateset import WorkflowJobGroupCoordinateSet


if sys.version_info.major == 2:
    input = raw_input


@receiver(post_migrate)
def add_view_user_permission(sender, **kwargs):
    """
    Adding the permission to view users in migrations. Other approaches
    include using another model and referencing Django's
    User model or using a proxy model after bug in Django
    https://code.djangoproject.com/ticket/11154 is resolved.
    """
    # don't set permissions in test database
    if not settings.TEST and sender.name == 'guardian':
        content_type = ContentType.objects.get(app_label='auth', model='user')
        Permission.objects.get_or_create(codename='view_user', name='View User', content_type=content_type)

        group = Group.objects.get_or_create(name="view_user_permission")
        # if the group is just created, add all users to it and give them view permission
        if group[1]:
            group = group[0]
            for user in User.objects.all():
                user.groups.add(group)
                assign_perm('view_user', group, user)


@receiver(post_migrate)
def update_rodan_jobs(sender, **kwargs):
    """
    This function is executed after the post-migrate signal.
    It registers or updates the database registry of Rodan jobs.
    """
    if sender.name != "rodan":
        return
    setattr(settings, "_update_rodan_jobs", True)
    import rodan.jobs.load  # noqa


@receiver(post_migrate)
def update_database_trigger(sender, **kwargs):
    """
    This function is executed after the post-migrate signal.
    It first connects to the Postgres database using psycopg2.
    It then loops through all tables that begin with 'rodan_',
    destroys triggers if they already exist in that table, and then creates the triggers.
    After each INSERT, UPDATE, or DELETE action, a message containing information with the
    status, the model name and the uuid will be published through Redis.
    """
    if sender.name != "rodan":
        return

    # don't register triggers in test database
    if settings.TEST:
        return

    conn = psycopg2.connect(
        database=settings.DATABASES['default']['NAME'],
        host=settings.DATABASES['default']['HOST'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD']
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    curs = conn.cursor()

    # Python function to add message to redis
    publish_message = '''
        CREATE OR REPLACE LANGUAGE plpythonu;
        CREATE OR REPLACE FUNCTION publish_message(notify text) RETURNS void AS $$
            import json
            import redis
            info = notify.split('/')
            status = info[0]
            if len(info) > 3:
                project = info[3]
            else:
                project = None
            model = info[1].replace('rodan_','')
            uuid = info[2].replace('-','')
            if project is not None:
                data = {{
                    'status': status,
                    'project': project,
                    'model': model,
                    'uuid': uuid
                }}
            else:
                 data = {{
                    'status': status,
                    'model': model,
                    'uuid': uuid
                }}
            r = redis.StrictRedis("{0}", {1}, db={2})
            r.publish('rodan:broadcast:rodan', json.dumps(data))
        $$ LANGUAGE plpythonu;
        GRANT EXECUTE ON FUNCTION publish_message(notify text) TO {3};
    '''.format(
        settings.WS4REDIS_CONNECTION['host'],
        settings.WS4REDIS_CONNECTION['port'],
        settings.WS4REDIS_CONNECTION['db'],
        settings.DATABASES['default']['USER']
    )

    # Testing publish_message function
    test_publish_message = '''
        SELECT "publish_message"('test/test/00000000000000000000000000000000');
    '''

    # Create trigger that sends information about the status, the table name, and the uuid of the modified element
    trigger = '''
        CREATE OR REPLACE FUNCTION object_notify() RETURNS trigger AS $$
        DECLARE
            status text;
            notify text;
        BEGIN
            IF (TG_OP = 'INSERT') THEN
                status = 'created';
                IF EXISTS (SELECT 1 FROM information_schema.columns WHERE TABLE_NAME=TG_TABLE_NAME AND COLUMN_NAME = 'project_id') THEN
                    notify = status || '/' || CAST(TG_TABLE_NAME AS text) || '/' || CAST(NEW.uuid AS text) || '/' || CAST(NEW.project_id AS text);
                ELSE
                    notify = status || '/' || CAST(TG_TABLE_NAME AS text) || '/' || CAST(NEW.uuid AS text);
                END IF;
                PERFORM publish_message(notify);
                RETURN NEW;
            ELSIF (TG_OP = 'UPDATE') THEN
                status = 'updated';
                IF EXISTS (SELECT 1 FROM information_schema.columns WHERE TABLE_NAME=TG_TABLE_NAME AND COLUMN_NAME = 'project_id') THEN
                    notify = status || '/' || CAST(TG_TABLE_NAME AS text) || '/' || CAST(NEW.uuid AS text) || '/' || CAST(NEW.project_id AS text);
                ELSE
                    notify = status || '/' || CAST(TG_TABLE_NAME AS text) || '/' || CAST(NEW.uuid AS text);
                END IF;
                PERFORM publish_message(notify);
                RETURN NEW;
            ELSIF (TG_OP = 'DELETE') THEN
                status = 'deleted';
                IF EXISTS (SELECT 1 FROM information_schema.columns WHERE TABLE_NAME=TG_TABLE_NAME AND COLUMN_NAME = 'project_id') THEN
                    notify = status || '/' || CAST(TG_TABLE_NAME AS text) || '/' || CAST(OLD.uuid AS text) || '/' || CAST(OLD.project_id AS text);
                ELSE
                    notify = status || '/' || CAST(TG_TABLE_NAME AS text) || '/' || CAST(OLD.uuid AS text);
                END IF;
                PERFORM publish_message(notify);
                RETURN OLD;
            END IF;
        END;
        $$ LANGUAGE plpgsql;
    '''

    # Loop through selected models to create trigger, if the trigger already exists, it gets destroyed before a new one
    # is created
    create_trigger = '''
        CREATE OR REPLACE FUNCTION name() RETURNS void AS $$
        DECLARE
            tablename name;
        BEGIN
            FOR tablename IN
                SELECT table_name FROM information_schema.tables
                WHERE table_schema='public' AND table_type='BASE TABLE'
                AND table_name SIMILAR TO 'rodan_[a-z]+'
            LOOP
                EXECUTE format('DROP TRIGGER IF EXISTS object_post_insert_notify ON %I', tablename);
                EXECUTE format('CREATE TRIGGER object_post_insert_notify AFTER INSERT OR UPDATE OR DELETE ON %I FOR EACH ROW EXECUTE PROCEDURE object_notify()', tablename);
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
        SELECT name();
        DROP FUNCTION name();
    '''

    try:
        curs.execute(publish_message)
    except psycopg2.ProgrammingError as e:
        if 'superuser' in str(e):
            # needs database superuser
            traceback.print_exc()
            solved = False

            while not solved:
                choice = '?'

                # If there are environment variables, don't ask from user due to stdin reading issue of Python
                # raw_input.
                if 'RODAN_PSQL_SUPERUSER_USERNAME' in os.environ and 'RODAN_PSQL_SUPERUSER_PASSWORD' in os.environ:
                    print("Environment variables RODAN_PSQL_SUPERUSER_USERNAME and RODAN_PSQL_SUPERUSER_PASSWORD detected.")  # noqa
                    choice = '1'
                elif 'RODAN_PSQL_SUPERUSER_COMMAND' in os.environ:
                    print("Environment variables RODAN_PSQL_SUPERUSER_COMMAND detected.")
                    choice = '2'

                while choice not in ('1', '2'):
                    print("================================================================")
                    print("Rodan needs PostgreSQL superuser permission to proceed. Options:")
                    print("  1. Provide the username and password of a superuser.")
                    print("  2. Provide the shell command to log in PostgreSQL console as a superuser (typically `sudo -u postgres psql --dbname={0}`)".format(settings.DATABASES['default']['NAME']))  # noqa
                    print("(Please inform Rodan developers if there is another way of connecting to PostgreSQL.)")
                    choice = input("Choice: ")

                if choice == '1':
                    if 'RODAN_PSQL_SUPERUSER_USERNAME' in os.environ:
                        username = os.environ['RODAN_PSQL_SUPERUSER_USERNAME']
                        del os.environ['RODAN_PSQL_SUPERUSER_USERNAME']
                    else:
                        username = input("Username: ")

                    if 'RODAN_PSQL_SUPERUSER_PASSWORD' in os.environ:
                        password = os.environ['RODAN_PSQL_SUPERUSER_PASSWORD']
                        del os.environ['RODAN_PSQL_SUPERUSER_PASSWORD']
                    else:
                        password = getpass.getpass("Password: ")

                    try:
                        conn_sudo = psycopg2.connect(
                            database=settings.DATABASES['default']['NAME'],
                            user=username,
                            password=password,
                            host=settings.DATABASES['default']['HOST'],
                            port=settings.DATABASES['default']['PORT']
                        )
                        conn_sudo.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
                        cur_sudo = conn_sudo.cursor()
                        cur_sudo.execute(publish_message)
                        solved = True
                    except Exception as e:
                        traceback.print_exc()
                        continue

                elif choice == '2':
                    try:
                        if 'RODAN_PSQL_SUPERUSER_COMMAND' in os.environ:
                            cmd = os.environ['RODAN_PSQL_SUPERUSER_COMMAND']
                            del os.environ['RODAN_PSQL_SUPERUSER_COMMAND']
                        else:
                            cmd = input("Command: ")
                        p = subprocess.Popen(
                            cmd,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stdin=subprocess.PIPE,
                            stderr=subprocess.STDOUT
                        )
                        grep_stdout = p.communicate(input=publish_message)[0]
                        rc = p.returncode
                        print(grep_stdout)
                        if "ERROR:" in grep_stdout or rc != 0:
                            continue
                        else:
                            solved = True
                    except Exception as e:
                        traceback.print_exc()
                        continue
        else:
            raise

    try:
        curs.execute(test_publish_message)
    except psycopg2.InternalError as e:
        if 'No module named redis' in str(e):
            traceback.print_exc()
            print("================================================================")
            print("Please execute `pip install redis` as a system package (not in virtualenv) on the database server {0}.".format(settings.DATABASES['default']['HOST']))  # noqa
        elif 'redis' in str(e):
            traceback.print_exc()
            print("================================================================")
            print("Please start redis-server at {0}:{1}.".format(
                settings.WS4REDIS_CONNECTION['host'],
                settings.WS4REDIS_CONNECTION['port'])
            )
        else:
            raise
        sys.exit(2)

    print("Registering Rodan database triggers...",)
    curs.execute(trigger)
    curs.execute(create_trigger)

    # Prevent multiple execution of post-migrate signal (not sure why it happens)
    global update_database_trigger
    update_database_trigger = None
    print("OK")


# Assign permissions
# view_ permissions are added to the models. add/change/delete_ permissions are django-builtin.
@receiver(post_save, sender=Project)
def assign_perms_project(sender, instance, created, raw, using, update_fields, **kwargs):
    if created:
        model_name = sender._meta.model_name
        if instance.creator:
            assign_perm('view_{0}'.format(model_name), instance.creator, instance)
            assign_perm('change_{0}'.format(model_name), instance.creator, instance)
            assign_perm('delete_{0}'.format(model_name), instance.creator, instance)
            instance.admin_group.user_set.add(instance.creator)

        assign_perm('view_{0}'.format(model_name), instance.admin_group, instance)
        assign_perm('change_{0}'.format(model_name), instance.admin_group, instance)

        assign_perm('view_{0}'.format(model_name), instance.worker_group, instance)


@receiver(post_save, sender=Workflow)
@receiver(post_save, sender=WorkflowRun)
@receiver(post_save, sender=Resource)
@receiver(post_save, sender=ResourceList)
@receiver(post_save, sender=WorkflowJob)
@receiver(post_save, sender=WorkflowJobGroup)
@receiver(post_save, sender=InputPort)
@receiver(post_save, sender=OutputPort)
@receiver(post_save, sender=WorkflowJobCoordinateSet)
@receiver(post_save, sender=WorkflowJobGroupCoordinateSet)
@receiver(post_save, sender=Connection)
@receiver(post_save, sender=RunJob)
@receiver(post_save, sender=ResultsPackage)
@receiver(post_save, sender=Input)
@receiver(post_save, sender=Output)
def assign_perms_others(sender, instance, created, raw, using, update_fields, **kwargs):
    if created:
        model_name = sender._meta.model_name

        # locate project
        if sender in (Workflow, WorkflowRun, Resource, ResourceList):
            project = instance.project
        elif sender in (WorkflowJob, WorkflowJobGroup):
            project = instance.workflow.project
        elif sender in (InputPort, OutputPort, WorkflowJobCoordinateSet):
            project = instance.workflow_job.workflow.project
        elif sender in (WorkflowJobGroupCoordinateSet, ):
            project = instance.workflow_job_group.workflow.project
        elif sender in (Connection, ):
            project = instance.input_port.workflow_job.workflow.project
        elif sender in (RunJob, ResultsPackage):
            project = instance.workflow_run.project
        elif sender in (Input, Output, ):
            project = instance.run_job.workflow_run.project

        admin_group = project.admin_group
        worker_group = project.worker_group

        # assign permissions
        assign_perm('view_{0}'.format(model_name), admin_group, instance)
        assign_perm('add_{0}'.format(model_name), admin_group, instance)
        assign_perm('change_{0}'.format(model_name), admin_group, instance)
        assign_perm('delete_{0}'.format(model_name), admin_group, instance)
        assign_perm('view_{0}'.format(model_name), worker_group, instance)
        assign_perm('add_{0}'.format(model_name), worker_group, instance)
        assign_perm('change_{0}'.format(model_name), worker_group, instance)
        assign_perm('delete_{0}'.format(model_name), worker_group, instance)


@receiver(post_save, sender=UserPreference)
@receiver(post_save, sender=User)
def assign_perms_user_userpreference(sender, instance, created, raw, using, update_fields, **kwargs):
    if created:
        model_name = sender._meta.model_name
        if sender == UserPreference:
            assign_perm('view_{0}'.format(model_name), instance.user, instance)
            assign_perm('change_{0}'.format(model_name), instance.user, instance)
            assign_perm('delete_{0}'.format(model_name), instance.user, instance)

        elif not settings.TEST:
            # add permission for viewing/changing/deleting the same user
            assign_perm('view_{0}'.format(model_name), instance, instance)
            assign_perm('change_{0}'.format(model_name), instance, instance)
            assign_perm('delete_{0}'.format(model_name), instance, instance)
            # add permission for viewing other users by adding it to view_user_permission group
            group = Group.objects.get_or_create(name="view_user_permission")[0]
            instance.groups.add(group)
            assign_perm('view_user', group, instance)
