from django.core.management.base import BaseCommand, CommandError
from rodan.models import ResourceType

def print_table(table):
    col_width = [min(max(len(x) for x in col), 35) for col in zip(*table)]
    print col_width
    for idx, line in enumerate(table):
        if idx == 1: # first line after table head
            print "-" * (sum(col_width)+3*len(col_width)+1)
        print "| " + " | ".join("{:{}}".format(str(x), col_width[i])
                                for i, x in enumerate(line)) + " |"

class Command(BaseCommand):
    help = 'Alter the description and/or extension of a Rodan resource type.'

    def handle(self, *args, **options):
        print "Here are the currently registered ResourceTypes in Rodan:"
        rt_table = [
            ['name', 'description', 'extension']
        ]
        for rt in ResourceType.objects.all().order_by('mimetype'):
            rt_table.append([rt.mimetype, rt.description, rt.extension])
        print_table(rt_table)

        rt = None
        while True:
            print ""
            rt_mimetype = raw_input("Type the name of the ResourceType that you would like to alter: ")
            try:
                rt = ResourceType.objects.get(mimetype=rt_mimetype)
                break
            except ResourceType.DoesNotExist:
                if rt_mimetype != '':
                    print "ResourceType {0} does not exist.".format(rt_mimetype)
                else:
                    pass

        print ""
        description = raw_input("Type the new description for {0} ({1}): ".format(rt.mimetype, rt.description))
        rt.description = description or rt.description
        extension = raw_input("Type the new extension for {0} ({1}): ".format(rt.mimetype, rt.extension))
        rt.extension = extension or rt.extension
        rt.save(update_fields=['description', 'extension'])

        print ""
        print "...updated."
