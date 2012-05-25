from celery.task import task

@task(name="mytaskname")
def add(x, y):
    return x + y
