import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rodan.settings")

from rodan.models.classifier import Classifier
from rodan.models.project import Project
from django.core.files import File


ProjectList = Project.objects.all()
print "Project List:"
for i, pr in enumerate(ProjectList):
    print str(i) + '. ' + pr.name

index = int(raw_input("Which project do you want to use: "))
classifier_project = ProjectList[index]
classifier_name = str(raw_input("Name your classifier: "))
cl = Classifier(project=classifier_project, name=classifier_name)
cl.save()

classifier_path = str(raw_input("Classifier path (drag and drop your classifier xml): ")).strip()
with open(classifier_path) as f:
    cl.classifier_file.save("idontcare.xml", File(f))

print "Success!"
print "Classifier UUID is " + str(cl.uuid)
