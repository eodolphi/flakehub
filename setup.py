#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'flask==0.10.1', 'flake8==2.4.1', 'gitpython==1.0.1', 'flask_restful==0.3.4'
]

test_requirements = [
    'pytest'
]

setup(
    name='flakehub',
    version='0.1.0',
    description="Automatically check the coding style of python projects on github",
    long_description=readme + '\n\n' + history,
    author="Ernst Odolphi",
    author_email='ernst.odolphi@gmail.com',
    url='https://github.com/eodolphi/flakehub',
    packages=[
        'flakehub',
    ],
    package_dir={'flakehub':
                 'flakehub'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='flakehub',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
