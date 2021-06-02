from rodan.jobs.interactive_classifier.wrapper import InteractiveClassifier
from rodan.jobs.resource_distributor import ResourceDistributor
from rodan.jobs.helloworld.helloworld import HelloWorld3
from rodan.jobs.labeler import Labeler
from rodan.celery import app

def run_register_jobs():
    # Python2 jobs
    app.register_task(InteractiveClassifier())

    # Python3 jobs
    app.register_task(HelloWorld3())

    # Core jobs
    app.register_task(ResourceDistributor())
    app.register_task(Labeler())

if __name__ == "__main__":
    run_register_jobs()