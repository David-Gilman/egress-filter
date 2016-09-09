
import os
from setuptools import setup, find_packages


# Create release using: python setup.py sdist --format=zip
# When creating a release please also merge to master and add a tag in the format "Release-1.0.0"


def read(fname):
    """
    Utility function to read the README file.
    Used for the long_description.  It's nice, because now 1) we have a top level
    README file and 2) it's easier to type in the README file than to put a raw
    string in below ...

    :param fname: Filename to read

    :return: file pointer
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name=u"Python Module Template",

    version=u"0.0.1",
    author=u"Oli Davis",
    author_email=u"oli.davis@me.com",
    url=u'https://bitbucket.org/davisowb/owbd-python-module-template.git',

    packages=find_packages(),

    description=u"Template for creating python modules.",
    long_description=read(u'README.md'),

    # Dependencies
    install_requires=[
        u'pip>=8.1.2'
    ],

    # Reference any non-python files to be included here
    package_data={
        '': ['*.md', '*.db', '*.txt'],  # Include all files from any package that contains *.db/*.md/*.txt
        'example_module.resources': ['*.*', '**/*.*', '**/**/*.*'],  # Folders up to 2 levels deep will be included
    },

    # List any scripts that are to be deployed to the python scripts folder
    scripts=[
        'example_script.py'
    ]

)
