
import os
from setuptools import setup, find_packages


VERSION = u'0.0.1'


def read(filename):

    """
    Utility function used to read the README file into the long_description.

    :param filename: Filename to read

    :return: file pointer
    """

    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name=u"example_module",  # The module name must match this!

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=VERSION,

    author=u"Oli Davis",
    author_email=u"oli.davis@me.com",

    license=u'MIT',

    url=u'https://bitbucket.org/davisowb/owbd-python-module-template.git',  # Use the url to the git repo
    download_url=u'https://bitbucket.org/davisowb/'
                 u'owbd-python-module-template.git/get/{version}.tar'.format(version=VERSION),

    packages=find_packages(),

    # If you want to distribute just a my_module.py, uncomment
    # this and comment out packages:
    #   py_modules=["my_module"],

    description=u"Template for creating python modules.",
    long_description=read(u'README.rst'),

    keywords=[u'example'],

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project?
        #   Development Status :: 1 - Planning
        #   Development Status :: 2 - Pre-Alpha
        #   Development Status :: 3 - Alpha
        #   Development Status :: 4 - Beta
        #   Development Status :: 5 - Production/Stable
        #   Development Status :: 6 - Mature
        #   Development Status :: 7 - Inactive
        u'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        u'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        u'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        u'Programming Language :: Python :: 2',
        u'Programming Language :: Python :: 2.7',

        u'Topic :: Utilities',
    ],

    # Dependencies
    install_requires=[
        u'pip>=8.1.2'
    ],

    # Reference any non-python files to be included here
    package_data={
        '': ['*.md', '*.rst', '*.db', '*.txt'],  # Include all files from any package that contains *.db/*.md/*.txt
        'example_module.resources': ['*.*', '**/*.*', '**/**/*.*'],  # Folders up to 2 levels deep will be included
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'example_script=example_module:main',
        ],
    },

    # List any scripts that are to be deployed to the python scripts folder
    scripts=[
        'example_script.py'
    ]

)
