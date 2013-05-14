#!/usr/bin/env python
from setuptools import setup, find_packages


version = __import__("partialize").__version__


setup(
    name="partialize",
    version=version,
    description="Python partial on steroids",
    author="Jonas Lundberg",
    author_email="jonas@5monkeys.se",
    url="https://github.com/5monkeys/partialize",
    download_url="https://github.com/5monkeys/partialize/tarball/v%s" % version,
    keywords=["partial", "functools", "args", "kwargs", "keywords", "arguments"],
    platforms=["any"],
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    tests_require=[],
    test_suite="tests",
)
