# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
# sys.path.append(os.path.abspath('../..'))
# sys.path.append(os.path.abspath('..'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rodan.settings')

# Rodan Initialization
os.environ["CELERY_JOB_QUEUE"] = "Docs"
os.environ["DJANGO_ALLOWED_HOSTS"] = "*"
os.environ["DJANGO_SECRET_KEY"] = "*"
os.environ["DJANGO_ACCESS_LOG"] = "*"
os.environ["DJANGO_DEBUG_LOG"] = "*"

# Setup Django
import django
django.setup()


# -- Project information -----------------------------------------------------

project = 'Rodan'
copyright = '2020, Distributed Digital Music Archives & Libraries Lab'
author = 'Andrew Hankinson'

# The full version, including alpha/beta/rc tags
release = '1.2.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['m2r', 'sphinx.ext.autodoc']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
autosectionlabel_prefix_document = True
autoclass_content = "both"
source_suffix = ['.rst', '.md']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']