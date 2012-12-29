# -*- coding: utf-8 *-*
try:
    from setuptools import setup
except ImportError:
    from distutils import setup


long_description = open("README.rst").read()

setup(
    name='mongolog',
    version='0.1.0',
    description='Centralized logging made simple using mongodb',
    long_description=long_description,
    author='Andrei Savu',
    author_email='contact@andreisavu.ro',
    maintainer='Jorge Puente Sarrín',
    maintainer_email="puentesarrin@gmail.com",
    url='https://github.com/puentesarrin/mongodb-log',
    packages=['mongolog'],
    keywords=["mongolog", "logging", "mongo", "mongodb"],
    install_requires=['pymongo'],
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: System :: Logging",
        "Topic :: Database"],
)
