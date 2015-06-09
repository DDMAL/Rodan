from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Update Rodan jobs.'

    def handle(self, *args, **options):
        from django.conf import settings
        setattr(settings, "_rodan_update_jobs", True)
        import rodan.jobs.load
