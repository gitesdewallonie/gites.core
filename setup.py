from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='gites.core',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
      open(os.path.join("docs", "HISTORY.txt")).read(),

      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='',
      author='Affinitic',
      author_email='info@affinitic.be',
      url='https://github.com/gitesdewallonie/gites.core',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['gites'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'lovely.memcached',
          'Products.LinguaPlone',
          'affinitic.caching',
          'affinitic.pwmanager',
          'collective.js.jqueryui',
          'collective.z3cform.datepicker',
          'five.grok',
          'gites.db',
          'monet.mapsviewlet',
          'plone.z3cform',
          'z3c.amf',
          'z3c.form',
          'z3c.sqlalchemy',
          'z3c.unconfigure',
          'zope.ramcache'],
      extras_require=dict(
          scripts=[]),
      entry_points={
          'console_scripts': [
              'groupement_update = gites.core.scripts.groupement_update:main',
              'geometry_columns_update = gites.core.scripts.geometry_columns_update:main',
          ]}
      )
