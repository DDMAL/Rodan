Rodan
=====

Rodan is a web-based document recognition system.


Building Rodan
--------------

You should check out the latest version from GitHub. In these instructions, $RODAN_HOME is the directory where you have checked out the Rodan source code.

Rodan uses [Celery](http://www.celeryproject.org) for performing all image manipulation operations. Celery uses the RabbitMQ back-end for message passing. You should follow the [instructions for installing RabbitMQ on your machine](http://www.rabbitmq.com/download.html).

### Python Server

We're using [virtualenv](http://www.virtualenv.org/en/latest/) to manage the server environment.

to install it:

    $> sudo pip install virtualenv

Create a virtual environment:

In your checked out directory, run

    $> virtualenv --no-site-packages rodan_env

Activate your virtual environment:

    $> source rodan_env/bin/activate

Install all the dependencies:

    $> pip install -r requirements.txt

Note: You may receive a message like this:

    $> Downloading/unpacking background-estimation==2.2.0pre2 (from -r requirements.txt (line 12))
    $>   Could not find any downloads that satisfy the requirement background-estimation==2.2.0pre2 (from -r requirements.txt (line 12))
    $> No distributions at all found for background-estimation==2.2.0pre2 (from -r requirements.txt (line 12))
    $> Storing complete log in /Users/$YOUR_HOME/.pip/pip.log

PIP was not able to install a package because it does not know from where to download it.  To bypass the installation of this requirement, edit `$RODAN_HOME/requirements.txt` and comment out (`#`) the line with the requirement and rerun the PIP install.  This may happen for multiple packages.

When this installs successfully, you should edit the `$RODAN_HOME/rodan/settings_production.py` file to correspond with your environment. For beginning development, the default sqlite3 database settings should be fine; however, you may wish to move to a more complete database system like Postgresql.

Once you have verified your settings, you can sync the Rodan models with the database. Since we are using the [South](http://south.aeracode.org) module for migrations, this is slightly different than "regular" Django:

    $> cd $RODAN_HOME
    $> python manage.py syncdb
    $> python manage.py migrate

If you run into errors about database key dependencies you can migrate two of the apps individually.

    $> python manage.py migrate djcelery
    $> python manage.py migrate rodan

### Celery Queue

You should set up Celery and RabbitMQ as necessary. If you just want the default account information that comes with Rodan, you should set up RabbitMQ like this:
    
    $> rabbitmqctl add_user rodanuser DDMALrodan
    $> rabbitmqctl add_vhost DDMAL
    $> rabbitmqctl set_permissions -p DDMAL rodanuser ".*" ".*" ".*"

This corresponds to the following default setting in `settings_production.py`.

    BROKER_URL = 'amqp://rodanuser:DDMALrodan@localhost:5672/DDMAL'

Which follows the pattern:

    amqp://$USER:$PASSWORD@$HOST:$PORT/$VHOST

### Cappuccino client

The Rodan interface is built using [Cappuccino](http://www.cappuccino-project.org).  You must first follow the instructions for getting and building Cappuccino.  This is usually accomplished by the following, but double-check with the Cappuccino documentation:

    $> git clone git://github.com/cappuccino/cappuccino.git
    $> ulimit -n 1024
    $> cd cappuccino
    $> jake sudo-install

This (1) grabs the source from Cappuccinos Git repo, (2) increases the number of open resources we will allow to 1024, and finally (3) does an Obj-J "make" and install on cappuccino.  Again, make sure to READ THE CAPPUCCINO DOCUMENTATION for the most up-to-date build and install instructions.

After Cappuccino is installed, you must link the compiled Frameworks into the Rodan client:

    $> cd $RODAN_HOME/client
    $> capp gen -l -f Rodan

This will create symlinks inside of the `Frameworks` folder to the compiled versions of the Cappuccino frameworks.

Next, you must create a symlink between the Rodan client and the Django server. (This is for development; in production, the client interface may be served separately from the Django web application).

    $> cd $RODAN_HOME/rodan/static
    $> ln -s ../../client/Rodan .

### Gamera

Currently, Rodan comes configured with support for the [Gamera](http://gamera.informatik.hsnr.de) toolkit. You should download the source code and, ensuring you are still within your Rodan virtual environment, install it with the following command:

    $> python setup.py install --nowx

This command installs Gamera without the GUI, since we are only interested in the Gamera image processing modules. Once you have installed this, you can install a number of optional Gamera modules:

#### The Musicstaves toolkit

The [Musicstaves toolkit](http://gamera.informatik.hsnr.de/addons/musicstaves/) contains a number of functions for working with printed music scores. To install it you will need to download it and install it within your Rodan virtualenv. If you get an error about a missing header file, you will need to add a CFLAGS option to your installation command that contains a reference to the `includes` folder in your Gamera source. Thus, you might install it like this:

    $> cd $MUSICSTAVES_DOWNLOAD_LOCATION
    $> CFLAGS="-I/path/to/gamera/gamera/includes" python setup.py install

#### Document Preprocessing Toolkits

These are four modules that offer some further document processing functionality. [Check out the code](http://github.com/DDMAL/document-preprocessing-toolkit), and then install each of the four modules individually. You will also likely need to install using the CFLAGS option demonstrated above. You should also make sure you install the `lyric_extraction` module last, since it depends on functions in other modules.

#### Rodan plugins

Finally, you should install the [Rodan plugins module](http://github.com/DDMAL/rodan_plugins), a set of Gamera plugins that replace built-in Gamera modules to allow them to operate with input/output, rather than modifying an image in-place. Install this in the same way as the previous modules.



Running Rodan
--------------

From $RODAN_HOME, make sure to activate the virtual environment:

    $> source rodan_env/bin/activate

Next, start the server:

    $> python manage.py runserver_plus

([`runserver_plus`](http://pythonhosted.org/django-extensions/runserver_plus.html) is installed via the Django-extensions module, and has several advantages over the "regular" Django `runserver` command.)

Next, start celery:

    $> python manage.py celery worker --loglevel=info -E

Open your browser and open `http://localhost:8000` to test your install.