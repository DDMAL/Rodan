from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import psycopg2
import psycopg2.extensions
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage
import json
import datetime
import os

class Command(BaseCommand):
    help = 'Running the command update_database will work as a daemon running in the backend and any update in the database will trigger a notification that will be broadcasted as a Redis message.'

    def handle(self, *args, **options):
        setattr(settings, "_update_database", True)

        def notify_socket_subscribers(notify):
            ''' Convert the notify message into a Redis message and broadcast to all subscribers '''

            publisher = RedisPublisher(facility='rodan', broadcast=True)
            info = notify.split('/')
            status = info[0]
            model = info[1]
            model = model.replace('rodan_', '')
            uuid = info[2]
            uuid = uuid.replace('-', '')

            data = {
                'status': status,
                'model': model,
                'uuid': uuid
            }
            message = RedisMessage(json.dumps(data))
            publisher.publish_message(message) 

        def handle_notification(notify):
            ''' Send the notify message to Redis message queue, and print the notification with the time '''

            notify_socket_subscribers(notify.payload) 
            print "Got NOTIFY:", notify.pid, notify.channel, notify.payload
            print datetime.datetime.now().time()
        
        conn = psycopg2.connect(database="postgres", host=os.environ.get('HOSTNAME'), user=os.environ.get('USER'), password="")
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        curs = conn.cursor()

        # Print all tables inside the database
        curs.execute("""SELECT *
          FROM information_schema.tables
          WHERE table_schema='public'
          ;""")
        print curs.fetchall()
        curs.execute('LISTEN "test";')
        print "Waiting for notifications on channel 'test'"

        # Create trigger that sends information about the status, the table name, and the uuid of the modified element
        trigger = '''
            CREATE OR REPLACE FUNCTION object_notify() RETURNS trigger AS $$
            DECLARE
                status text;
            BEGIN
                IF (TG_OP = 'INSERT') THEN
                    status = 'created';
                ELSIF (TG_OP = 'UPDATE') THEN
                    status = 'updated';
                ELSIF (TG_OP = 'DELETE') THEN
                    status = 'deleted';
                END IF;
                PERFORM pg_notify('test', status || '/' || CAST(TG_TABLE_NAME AS text) || '/' || CAST(NEW.uuid AS text));
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            '''

        # Loop through selected models to create trigger, if the trigger already exists, it gets destroyed before a new one is created
        create_trigger = '''
            CREATE OR REPLACE FUNCTION name() RETURNS void AS $$
            DECLARE
                tablename text;
            BEGIN
                FOR tablename IN
                    SELECT table_name FROM information_schema.tables
                    WHERE table_schema='public' AND table_type='BASE TABLE'
                    AND table_name LIKE 'rodan_%'
                    LOOP
                        DROP TRIGGER IF EXISTS object_post_insert_notify ON tablename;
                        CREATE TRIGGER object_post_insert_notify AFTER INSERT OR UPDATE ON tablename FOR EACH ROW EXECUTE PROCEDURE object_notify();
                    END LOOP;
            END;
            $$ LANGUAGE plpgsql;
        '''

        curs.execute(trigger)
        curs.execute(create_trigger)

        while True:
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop()
                handle_notification(notify)
