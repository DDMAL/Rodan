from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import psycopg2
import psycopg2.extensions
import os


class Command(BaseCommand):
    help = 'Running the command update_database will work as a daemon running in the backend and any update in the database will trigger a notification that will be broadcasted as a Redis message.'

    def handle(self, *args, **options):
        setattr(settings, "_update_database", True)

        conn = psycopg2.connect(database="postgres", host=os.environ.get('HOSTNAME'), user=os.environ.get('USER'), password="")
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        curs = conn.cursor()

        curs.execute('LISTEN "test";')
        print "Waiting for notifications on channel 'test'"

        print_notify = '''
            CREATE OR REPLACE FUNCTION print_notify(notify text) RETURNS void AS $$
                import datetime
                import os
                import sys
                import json
                import redis
                import socket

                info = notify.split('/')
                status = info[0]
                model = info[1].replace('rodan_','')
                uuid = info[2].replace('-','')

                data = {
                    'status': status,
                    'model': model,
                    'uuid': uuid
                }

                try:
                    HOSTNAME = socket.gethostname()
                except:
                    HOSTNAME = 'localhost'

                PORT = 6379

                r = redis.StrictRedis(HOSTNAME, PORT, db=0)
                r.publish('rodan:broadcast:rodan', json.dumps(data))

                print "Got NOTIFY:", notify
                print datetime.datetime.now().time()

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
                -- PERFORM pg_notify('test', notify);
                PERFORM print_notify(notify);
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

        curs.execute(print_notify)
        curs.execute(trigger)
        curs.execute(create_trigger)
