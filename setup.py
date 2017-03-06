# import os
from setuptools import setup, find_packages

# README = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
# REQUIRES = [i.strip() for i in open("requirements.txt").readlines()]

# allow setup.py to be run from any path
# os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

__version__ = '0.1.0'
__description__ = 'Liberia de Trotamundia para Django',
__license__ = 'BSD'
__author__ = 'Juan Ortiz',
__email__ = 'juan.ortiz@trotamundia.com',


setup(
    name='trotamundiaCore',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    license=__license__,
    description=__description__,
    url='http://www.trotamundia.com/',
    author=__author__,
    author_email=__email__,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=['django'],
    # dependency_links=[
    #     'git+https://gianburga@bitbucket.org/gianburga/django-oauth-toolkit-mongoengine.git',
    #     'git+https://github.com/MongoEngine/django-mongoengine.git',
    #     'git+https://github.com/gianburga/culqi-python.git',
    # ]
)