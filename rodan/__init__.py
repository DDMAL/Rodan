"""
  ()_()      .-.        _               \\\  ///
  (O o)    c(O_O)c     /||_       /)    ((O)(O))
   |^_\   ,'.---.`,     /o_)    (o)(O)   | \ ||
   |(_)) / /|_|_|\ \   / |(\     //\\    ||\\||
   |  /  | \_____/ |   | | ))   |(__)|   || \ |
   )|\\  '. `---' .`   | |//    /,-. |   ||  ||
  (/  \)   `-...-'     \__/    -'   ''  (_/  \_)
"""
from __future__ import absolute_import


__title__ = "Rodan"

# Module version following PEP 396
# Get version: import rodan; rodan.__version__
__version__ = "1.1.2"

__copyright__ = "Copyright 2011-2016 Distributed Digital Music Archives & Libraries Lab"


# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app
