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

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import psycopg2
import psycopg2.extensions
import os

'''
This function is executed after the post-migrate signal.
It first connects to the Postgres database using psycopg2.
It then loops through all tables that begin with 'rodan_', destroys triggers if they already exist in that table, and then creates the triggers.
After each INSERT, UPDATE, or DELETE action, a message containing information with the status, the model name and the uuid will be published through Redis.
'''
@receiver(post_migrate)
def update_database(sender, **kwargs):

    conn = psycopg2.connect(database=settings.DATABASES['default']['NAME'], host=settings.REDIS_HOST, user=settings.DATABASES['default']['USER'], password=settings.DATABASES['default']['PASSWORD'])
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    curs = conn.cursor()

    publish_message = '''
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

            r = redis.StrictRedis("{0}", {1}, db={2})
            r.publish('rodan:broadcast:rodan', json.dumps(data))

        $$ LANGUAGE plpythonu;
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
            ELSIF (TG_OP = 'UPDATE') THEN
                status = 'updated';
            ELSIF (TG_OP = 'DELETE') THEN
                status = 'deleted';
            END IF;
            notify = status || '/' || CAST(TG_TABLE_NAME AS text) || '/' || CAST(NEW.uuid AS text);
            PERFORM publish_message(notify);
            RETURN NEW;
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
                AND table_name LIKE 'rodan_%'
            LOOP
                EXECUTE format('DROP TRIGGER IF EXISTS object_post_insert_notify ON %I', tablename);
                EXECUTE format('CREATE TRIGGER object_post_insert_notify AFTER INSERT OR UPDATE ON %I FOR EACH ROW EXECUTE PROCEDURE object_notify()', tablename);
            END LOOP;
        END;
        $$ LANGUAGE plpgsql;
        SELECT name();
        '''

    curs.execute(publish_message.format(settings.REDIS_HOST, settings.REDIS_PORT, settings.DB))
    curs.execute(trigger)
    curs.execute(create_trigger)
