Rodan
=====

Readme under construction. Will contain list of dependencies, usage instructions, explanation of the file structure, etc.

Dependencies
------------

* Django 1.4 (installed on Susato)
* Python 2.7 (also installed on Susato)
* PostgreSQL (maybe sqlite for individual development)

Instructions
------------

* Check out the source with `git clone git@github.com:DDMAL/Rodan.git rodan`
* `cd` into the rodan directory
* `python manage.py syncdb` should do all the database stuff for you
* `python manage.py runserver`. If you're running it on susato and want to be able to access it remotely, pick a port (e.g. 8001) and do something like this: `python manage.py runserver 0.0.0.0:8001`. You can now access your Django instance from http://rodan.simssa.ca:8001. If the port you're trying to use is already taken, use another one.

Project layout
-------------

Each of the 5 components (correction, display, processing, projects, recognition) exists as a separate app. The `rodan` directory just contains project-specific settings and URLs. More coming
