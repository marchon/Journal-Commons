# -*- coding: utf-8 -*-
"""
This module contains the tool of journalcommons.Conference
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = read('version.txt')

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read("docs", "HISTORY.txt")
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('journalcommons', 'Conference', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

tests_require=['zope.testing']

setup(name='journalcommons.Conference',
      version=version,
      description="A product to organize conferences",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='conference',
      author='Journal Commmons',
      author_email='jcommons@jcommons.org',
      url='http://svn.plone.org/svn/plone/plone.example',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['journalcommons', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
			'Products.DataGridField<1.6.4',			# Until we migrate to Plone 4 and DataGrid 1.8
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'journalcommons.Conference.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*- 
      [distutils.setup_keywords]
      paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
      paster_plugins.txt = setuptools.command.egg_info:write_arg
      """,
      paster_plugins = ["ZopeSkel"],
      )
