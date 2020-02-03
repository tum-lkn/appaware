
"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='netstatspy',

    version='0.0.1',  # ToDo

    description='Project to read network statistics',

    long_description=long_description,

    long_description_content_type='text/markdown',

    url='https://github.com/pypa/sampleproject',  # ToDo

    author='Chair for Communication Networks, Technical University of Munich',

    author_email='benedikt.hess@tum.de',

    classifiers=[
        # Common values:
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
    ],

    keywords='statistics network interface ip ss tc ip queue',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=[],

    extras_require={
        'redis': ['redis'],
    },

    entry_points={
        'console_scripts': [
            'netstatspy=netstatspy:main',
        ],
    },

    # List additional URLs that are relevant to your project as a dict.
    #
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    #
    # Examples listed include a pattern for specifying where the package tracks
    # issues, where the source is hosted, where to say thanks to the package
    # maintainers, and where to support the project financially. The key is
    # what's used to render the link text on PyPI.
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/pypa/sampleproject/issues',
        'Source': 'https://github.com/pypa/sampleproject/',
    },  # ToDO
)
