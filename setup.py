# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup

import os


version = "0.6"

long_description = (
    open("README.rst").read()
    + "\n"
    + open(os.path.join("src", "plone", "jsonapi", "core", "docs", "Readme.txt")).read()
    + "\n"
    + open(os.path.join("docs", "HISTORY.rst")).read()
    + "\n"
)

setup(
    name="plone.jsonapi.core",
    version=version,
    description="Plone JSON API",
    long_description=long_description,
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: Zope2",
    ],
    keywords="",
    author="Ramon Bartl",
    author_email="rb@ridingbytes.com",
    url="https://github.com/collective/plone.jsonapi.core",
    license="MIT",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["plone", "plone.jsonapi"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "werkzeug>=0.7.2",
        "simplejson>=2.0.9",
        "dicttoxml"
        # -*- Extra requirements: -*-
    ],
    extras_require={"test": ["plone.app.testing", "unittest2",]},
    entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
