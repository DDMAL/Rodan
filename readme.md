Rodan
=====

Readme under construction. Will contain list of dependencies, usage instructions, explanation of the file structure, etc.

Dependencies
------------

* Django 1.4 (installed on Susato)
* Python 2.7 (also installed on Susato)
* PostgreSQL (sqlite for local development)
* Celery (installed on Susato)
* Solr
* [VIPS](http://www.vips.ecs.soton.ac.uk/index.php?title=VIPS) (installed on Susato; needed for diva)

Development
-----------

We're using virtualenv to manage dependencies

to install it: `sudo pip install virtualenv`

Create a virtual environment:

in your checked out directory, run

    virtualenv --no-site-packages rodan_env

Install all the dependencies:
    source rodan_env/bin/activate
    pip install -r requirements.txt

if you need to add a dependency, install it with pip then run

    pip freeze > requirements.txt

and commit the requirements file

### Other dependencies

Since gamera is not installable with pip, you have to download it from http://sourceforge.net/projects/gamera/
and then build the python module with `python setup.py build && sudo python setup.py install`

```
cd rodan_env/lib/python2.7/site-packages/
ln -s <python module directory>/gamera gamera
```

You will also need these plugins for gamera, which have to be added manually as well:

* MusicStaves Toolkit @ `http://gamera.informatik.hsnr.de/addons/musicstaves/index.html`
  Note that this plugin has an build error in the file <root dir of toolkit>/include/plugins/line_tracking.hpp
  To fix it, simply copy paste the "chord_length" function at the end of the file to the beginning of the file
  right after the preprocessor commands.

* Border-Removal @ `https://github.com/DDMAL/document-preprocessing-toolkit`
  ```
  cd <document-preprocessing-toolkit location>/border-removal
  python setup.py install
  ```

* libmei @ `https://github.com/gburlet/libmei/tree/solesmesbuild`
  Note that if you are getting `pymei` import errors, it is because you are missing `libmei` and not `pymei`.

* MUSIC21 is included in the pip requirements.txt, but it will not be installed correctly. You will need to:
```
cd <directory where you ran "pip install -r requirements.txt">/build/music21
chmod u+x installer.command
./installer.command
```
  to get MUSIC21 installed and working properly. Information regarding the installation process using installer.command
  can be found here `http://mit.edu/music21/doc/html/installMac.html#installmac`.
  After you have installed MUSIC21, you can remove the rodan_env/build directory
```
cd rodan_env
sudo rm -rf build
```

You'll also need to install VIPS (along with the Python bindings) for the diva module to work. The installation guide is probably somewhere on the [wiki](http://www.vips.ecs.soton.ac.uk/). If you don't want to install it, create a directory called `vipsCC` in the project root, containing an `__init__.py` file as well as a file called `VImage.py`. In `VImage.py`, write something like `VImage = ''`. That should be enough if you just need to get the system up and running and don't care if diva works or not. Just don't test the diva preprocessing job.

Setup
-----
* Install rabbitmq if required

Configure rabbitmq with

    /usr/local/sbin/rabbitmqctl add_user rodanuser DDMALrodan
    /usr/local/sbin/rabbitmqctl add_vhost DDMAL
    /usr/local/sbin/rabbitmqctl set_permissions -p DDMAL rodanuser ".*" ".*" ".*"

Instructions
------------

* Check out the source with `git clone git@github.com:DDMAL/Rodan.git rodan`
* `cd` into the rodan directory
* `source rodan_env/bin/activate` to setup the virtualenv
* `python manage.py syncdb` should do all the database stuff for you. Don't say yes when asked
   to create a superuser and a fixture will be created
* `python manage.py celeryd --loglevel=info` to start the celery broker
* `python manage.py celeryev --camera=rodan.monitor.Rodaonitor`
* `python manage.py runserver`. Access the site at http://localhost:8000
* If you're running it on susato and want to be able to access it remotely, pick a port
  (e.g. 8001) and do something like this: `python manage.py runserver 0.0.0.0:8001`.
  You can now access your Django instance from http://rodan.simssa.ca:8001. If the
  port you're trying to use is already taken, use another one.

Project layout
-------------

* `db.sqlite` - for development only. not tracked by git. created upon running `python manage.py syncdb`
* `__init__.py`
* `manage.py` - comes with Django. Not modified.
* `readme.md`
* `rodan/`
    * `__init__.py` - empty file, needed to be able to import the app
    * `settings.py` - the project-wide settings. should not need to be changed
    * `templates/` - all the template files will go under here. there will be a directory for each app.
    * `urls.py` - includes all the urls.py files for each app (e.g. `correction/urls.py`) and maps the base url to the `main` view defined in `views.py`
    * `views.py` - defines the `main` view, which either returns the `dashboard` view in `projects.views` or asks the user to register/login
