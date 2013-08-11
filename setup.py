# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

version = '0.2'

long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open(os.path.join('docs', 'CONTRIBUTORS.rst')).read()
    + '\n' +
    open(os.path.join('docs', 'HISTORY.rst')).read()
    + '\n')

setup(name='plone.jsonapi',
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
      keywords='',
      author='Ramon Bartl',
      author_email='ramon.bartl@googlemail.com',
      url='https://github.com/ramonski/plone.jsonapi',
      license='MIT',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'simplejson',
          'werkzeug',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

# vim: set ft=python ts=4 sw=4 expandtab :
