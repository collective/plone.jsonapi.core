# -*- coding: utf-8 -*-

import os

from setuptools import find_packages
from setuptools import setup


version = "0.8.1"

long_description = (
    open("README.md").read()
    + "\n"
    + open(os.path.join("docs", "HISTORY.rst")).read()
    + "\n"
)

setup(
    name="plone.jsonapi.core",
    version=version,
    description="An extensible Plone JSON API Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="plone jsonapi rest api json werkzeug",
    author="Ramon Bartl",
    author_email="rb@ridingbytes.com",
    url="https://github.com/collective/plone.jsonapi.core",
    license="GPLv2",
    packages=find_packages("src"),
    package_dir={"": "src"},
    namespace_packages=["plone", "plone.jsonapi"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        "six",
        # werkzeug 2.x and newer dicttoxml drop Python 2.7 support; cap
        # to the last releases that still install on py2.7.
        "werkzeug <2.0",
        "dicttoxml <=1.7.4",
    ],
    extras_require={"test": ["plone.app.testing", "unittest2"]},
    entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
