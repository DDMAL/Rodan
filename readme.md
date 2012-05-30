Rodan
=====

Readme under construction. Will contain list of dependencies, usage instructions, explanation of the file structure, etc.

Dependencies
------------

* Django 1.4 (installed on Susato)
* Python 2.7 (also installed on Susato)
* PostgreSQL (sqlite for local development)
* Celery (installed on Susato)

Development
-----------

We're using virtualenv to manage dependencies

to install it: `sudo pip install virtualenv`

Create a virtual environemnt:

in your checked out directory, run

    virtualenv --no-site-packages rodan_env

Install all the dependencies:
    source rodan_env/bin/activate
    pip install -r requirements.txt

if you need to add a dependency, install it with pip then run

    pip freeze > requirements.txt

and commit the requirements file

Setup
-----
* Install rabbitmq if required
* /usr/local/sbin/rabbitmqctl add_user rodanuser DDMALrodan
* /usr/local/sbin/rabbitmqctl add_vhost DDMAL
* /usr/local/sbin/rabbitmqctl set_permissions -p DDMAL rodanuser ".*" ".*" ".*"

Instructions
------------

* Check out the source with `git clone git@github.com:DDMAL/Rodan.git rodan`
* `cd` into the rodan directory
* `source rodan_env/bin/activate` to setup the virtualenv
* `python manage.py syncdb` should do all the database stuff for you. Don't say yes when asked
   to create a superuser and a fixture will be created
* `python manage.py celeryd --loglevel=info` to start the celery broker
* `python manage.py runserver`. Access the site at http://localhost:8000
* If you're running it on susato and want to be able to access it remotely, pick a port
  (e.g. 8001) and do something like this: `python manage.py runserver 0.0.0.0:8001`.
  You can now access your Django instance from http://rodan.simssa.ca:8001. If the
  port you're trying to use is already taken, use another one.

Project layout
-------------

Each of the 5 components (correction, display, processing, projects, recognition) exists as a separate app. The `rodan` directory just contains project-specific settings and URLs as well as some basic views (the main view, which either redirects the user to the dashboard or asks the user to sign up or login).

* `correction/`
* `db.sqlite` - for development only. not tracked by git. created upon running `python manage.py syncdb`
* `display/`
* `__init__.py`
* `manage.py` - comes with Django. Not modified.
* `projects/`
* `readme.md`
* `recognition/`
* `rodan/`
    * `__init__.py` - empty file, needed to be able to import the app
    * `settings.py` - the project-wide settings. should not need to be changed
    * `templates/` - all the template files will go under here. there will be a directory for each app.
    * `urls.py` - includes all the urls.py files for each app (e.g. `correction/urls.py`) and maps the base url to the `main` view defined in `views.py`
    * `views.py` - defines the `main` view, which either returns the `dashboard` view in `projects.views` or asks the user to register/login
