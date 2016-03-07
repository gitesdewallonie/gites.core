from setuptools import setup, find_packages
import os

version = '0.2.6.dev0'

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
          'Embedly',
          'Products.LinguaPlone',
          'Products.LocalFS',
          'affinitic.caching',
          'affinitic.pwmanager',
          'collective.cookiecuttr',
          'collective.fb',
          'collective.js.jqueryui',
          'collective.monkeypatcher',
          'collective.z3cform.datepicker',
          'five.grok',
          'gites.db',
          'gites.locales',
          'collective.captcha',
          'mobile.sniffer',
          'pygeocoder',
          'monet.mapsviewlet',
          'plone.z3cform',
          'sc.social.like',
          'plone.widgets',
          'z3c.form',
          'z3c.table',
          'gites.map',
          'z3c.sqlalchemy',
          'Products.SQLAlchemyDA',
          'z3c.unconfigure',
          'beautifulsoup4',
          'zope.ramcache',
          'gites.skin'],
      extras_require=dict(
          test=[
              'affinitic.testing',
              'unittest2',
              'zope.testing',
              'plone.app.testing'],
          scripts=[]),
      entry_points={
          'console_scripts': [
              'groupement_update = gites.core.scripts.groupement_update:main',
              'geometry_columns_update = gites.core.scripts.geometry_columns_update:main',
              'sort_order_update = gites.core.scripts.sort_order_update:main',
          ]}
      )
