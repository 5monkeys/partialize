#!/usr/bin/env python
from setuptools import setup, find_packages

version = '0.0.2'

setup(
    name='partialize',
    version=version,
    author="Jonas Lundberg",
    author_email="jonas@5monkeys.se",
    url="http://github.com/5monkeys/partialize",
    keywords=["functools", "partial"],
    platforms=["any"],
    license="MIT",
    packages=find_packages(),
    tests_require=[],
    test_suite="tests",
)
