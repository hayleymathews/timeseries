"""
setup file for timeseries package
"""
from setuptools import setup, find_packages


setup(name='timeseries',
      verson='0.1',
      description='basic functionality for timeseries operations',
      author='Hayley Mathews',
      author_email='hayley.e.mathews@gmail.com',
      url='https://bitbucket.org/hayley_mathews/timeseries',
      packages=find_packages(),
      install_requires=['numpy'],
      test_suite='nose.collector',
      tests_require=['nose'],
      )
