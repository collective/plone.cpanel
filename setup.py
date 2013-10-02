from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='plone.cpanel',
      version=version,
      description="Enables public creation of Plone sites",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
        ],
      keywords='plone saas',
      author='Dylan Jay',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.cpanel',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.browserpage',
          'zope.component',
          'zope.security',
          'zope.traversing',
      ],
      extras_require={
        'test': ['plone.app.testing', 'plone.app.robotframework'],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
