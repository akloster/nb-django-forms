
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Tools to use Django forms interactively inside the IPython Notebook',
    'author': 'Andreas Klostermann',
    'url': '',
    'download_url': '',
    'author_email': 'andreasklostermann@gmail.com',
    'version': '0.1',
    'install_requires': ['nose', 'django', 'ipython'],
    'packages': ['nb_django_forms'],
    'scripts': [],
    'name': 'nbdjangoforms'
}

setup(**config)
