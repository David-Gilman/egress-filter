
import os
from setuptools import setup, find_packages


def read(filename):

    """
    Utility function used to read the README file into the long_description.

    :param filename: Filename to read

    :return: file pointer
    """

    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name=u"example_module",  # The module name must match this!

    version=u"0.0.1",
    author=u"Oli Davis",
    author_email=u"oli.davis@me.com",
    url=u'https://bitbucket.org/davisowb/owbd-python-module-template.git',  # Use the url to the git repo
    download_url=u'https://bitbucket.org/davisowb/owbd-python-module-template.git/get/0.0.1.tar',

    packages=find_packages(),

    description=u"Template for creating python modules.",
    long_description=read(u'README.md'),

    keywords=[u'example'],
    classifiers=[],

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
