from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Any update in the database will trigger a notification.'

    def handle(self, *args, **options):
        from django.conf import settings
        setattr(settings, "_update_database", True)
        import psycopg2
        import psycopg2.extensions
        import datetime
        import os

        def handle_notification(notify):
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
        curs.execute('NOTIFY "test";')
        print "Waiting for notifications on channel 'test'"

        # Create trigger
        trigger = '''
            CREATE OR REPLACE FUNCTION object_notify() RETURNS trigger AS $$
            DECLARE
            BEGIN
                PERFORM pg_notify('test', CAST(NEW.name AS text));
                PERFORM pg_notify('test', CAST(NEW.uuid AS text));
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
