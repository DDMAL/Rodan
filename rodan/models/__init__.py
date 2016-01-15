from rodan.models.inputporttype import InputPortType
from rodan.models.outputporttype import OutputPortType
from rodan.models.inputport import InputPort
from rodan.models.outputport import OutputPort
from rodan.models.input import Input
from rodan.models.output import Output
from rodan.models.project import Project
from rodan.models.job import Job
from rodan.models.workflowjob import WorkflowJob
from rodan.models.workflow import Workflow
from rodan.models.workflowjobgroup import WorkflowJobGroup
from rodan.models.workflowrun import WorkflowRun
from rodan.models.runjob import RunJob
from rodan.models.resultspackage import ResultsPackage
from rodan.models.resource import Resource
from rodan.models.resourcetype import ResourceType
from rodan.models.connection import Connection
from rodan.models.workflowjobcoordinateset import WorkflowJobCoordinateSet

from guardian.shortcuts import assign_perm
from rest_framework.compat import get_model_name

from django.db.models.signals import post_migrate, pre_save, pre_delete, post_save, post_delete
from django.dispatch import receiver
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import psycopg2
import psycopg2.extensions
import os, sys
import traceback
import getpass
import subprocess

@receiver(post_migrate)
def update_rodan_jobs(sender, **kwargs):
    """
    This function is executed after the post-migrate signal.
    It registers or updates the database registry of Rodan jobs.
    """
    if sender.name != "rodan":
        return
    setattr(settings, "_update_rodan_jobs", True)
    import rodan.jobs.load

@receiver(post_migrate)
def update_database_trigger(sender, **kwargs):
    '''
    This function is executed after the post-migrate signal.
    It first connects to the Postgres database using psycopg2.
    It then loops through all tables that begin with 'rodan_', destroys triggers if they already exist in that table, and then creates the triggers.
    After each INSERT, UPDATE, or DELETE action, a message containing information with the status, the model name and the uuid will be published through Redis.
    '''
    if sender.name != "rodan":
        return

    # don't register triggers in test database
    if settings.TEST:
        return

    conn = psycopg2.connect(database=settings.DATABASES['default']['NAME'], host=settings.DATABASES['default']['HOST'], user=settings.DATABASES['default']['USER'], password=settings.DATABASES['default']['PASSWORD'])
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
            model = info[1].replace('rodan_','')
            uuid = info[2].replace('-','')
            data = {{
                'status': status,
                'model': model,
                'uuid': uuid
            }}
            r = redis.StrictRedis("localhost", {0}, db={1})
            r.publish('rodan:broadcast:rodan', json.dumps(data))
        $$ LANGUAGE plpythonu;
        GRANT EXECUTE ON FUNCTION publish_message(notify text) TO {2};
    '''.format(settings.DATABASES['default']['REDIS_PORT'], settings.DATABASES['default']['REDIS_DBNUMBER'], settings.DATABASES['default']['USER'])

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
                notify = status || '/' || CAST(TG_TABLE_NAME AS text) || '/' || CAST(NEW.uuid AS text);
                PERFORM publish_message(notify);
                RETURN NEW;
            ELSIF (TG_OP = 'UPDATE') THEN
                status = 'updated';
                notify = status || '/' || CAST(TG_TABLE_NAME AS text) || '/' || CAST(NEW.uuid AS text);
                PERFORM publish_message(notify);
                RETURN NEW;
            ELSIF (TG_OP = 'DELETE') THEN
                status = 'deleted';
                notify = status || '/' || CAST(TG_TABLE_NAME AS text) || '/' || CAST(OLD.uuid AS text);
                PERFORM publish_message(notify);
                RETURN OLD;
            END IF;
        END;
        $$ LANGUAGE plpgsql;
    '''

    # Loop through selected models to create trigger, if the trigger already exists, it gets destroyed before a new one is created
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

                # If there are environment variables, don't ask from user due to stdin reading issue of Python raw_input.
                if 'RODAN_PSQL_SUPERUSER_USERNAME' in os.environ and 'RODAN_PSQL_SUPERUSER_PASSWORD' in os.environ:
                    print "Environment variables RODAN_PSQL_SUPERUSER_USERNAME and RODAN_PSQL_SUPERUSER_PASSWORD detected."
                    choice = '1'
                elif 'RODAN_PSQL_SUPERUSER_COMMAND' in os.environ:
                    print "Environment variables RODAN_PSQL_SUPERUSER_COMMAND detected."
                    choice = '2'

                while choice not in ('1', '2'):
                    print "================================================================"
                    print "Rodan needs PostgreSQL superuser permission to proceed. Options:"
                    print "  1. Provide the username and password of a superuser."
                    print "  2. Provide the shell command to log in PostgreSQL console as a superuser (typically `sudo -u postgres psql --dbname={0}`)".format(settings.DATABASES['default']['NAME'])
                    print "(Please inform Rodan developers if there is another way of connecting to PostgreSQL.)"
                    choice = raw_input("Choice: ")

                if choice is '1':
                    if 'RODAN_PSQL_SUPERUSER_USERNAME' in os.environ:
                        username = os.environ['RODAN_PSQL_SUPERUSER_USERNAME']
                        del os.environ['RODAN_PSQL_SUPERUSER_USERNAME']
                    else:
                        username = raw_input("Username: ")

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

                elif choice is '2':
                    try:
                        if 'RODAN_PSQL_SUPERUSER_COMMAND' in os.environ:
                            cmd = os.environ['RODAN_PSQL_SUPERUSER_COMMAND']
                            del os.environ['RODAN_PSQL_SUPERUSER_COMMAND']
                        else:
                            cmd = raw_input("Command: ")
                        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
                        grep_stdout = p.communicate(input=publish_message)[0]
                        rc = p.returncode
                        print grep_stdout
                        if "ERROR:" in grep_stdout or rc is not 0:
                            continue
                        else:
                            solved = True
                    except Exception as e:
                        traceback.print_exc()
                        continue
        else:
            raise

    print ""

    try:
        curs.execute(test_publish_message)
    except psycopg2.InternalError as e:
        if 'No module named redis' in str(e):
            traceback.print_exc()
            print "================================================================"
            print "Please execute `pip install redis` as a system package (not in virtualenv) on the database server {0}.".format(settings.DATABASES['default']['HOST'])
        elif 'redis' in str(e):
            traceback.print_exc()
            print "================================================================"
            print "Please start redis-server at {0}:{1}.".format(settings.DATABASES['default']['HOST'], settings.DATABASES['default']['REDIS_PORT'])
        else:
            raise
        sys.exit(2)

    print "Registering Rodan database triggers...",
    curs.execute(trigger)
    curs.execute(create_trigger)

    # Prevent multiple execution of post-migrate signal (not sure why it happens)
    global update_database_trigger
    update_database_trigger = None
    print "OK"


# Assign permissions
## view_ permissions are added to the models. add/change/delete_ permissions are django-builtin.
@receiver(post_save, sender=Project)
def assign_perms_project(sender, instance, created, raw, using, update_fields, **kwargs):
    if created:
        model_name = get_model_name(sender)
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
@receiver(post_save, sender=WorkflowJob)
@receiver(post_save, sender=InputPort)
@receiver(post_save, sender=OutputPort)
@receiver(post_save, sender=WorkflowJobCoordinateSet)
@receiver(post_save, sender=Connection)
@receiver(post_save, sender=RunJob)
@receiver(post_save, sender=ResultsPackage)
@receiver(post_save, sender=Input)
@receiver(post_save, sender=Output)
def assign_perms_others(sender, instance, created, raw, using, update_fields, **kwargs):
    if created:
        model_name = get_model_name(sender)

        # locate project
        if sender in (Workflow, WorkflowRun, Resource):
            project = instance.project
        elif sender in (WorkflowJob,):
            project = instance.workflow.project
        elif sender in (InputPort, OutputPort, WorkflowJobCoordinateSet):
            project = instance.workflow_job.workflow.project
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
