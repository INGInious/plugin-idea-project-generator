#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import project_generator

setup(
    name="project_generator",
    version=project_generator.__version__,
    description="Plugin that generates IntelliJ projects",
    packages=find_packages(),
    install_requires=["inginious>=0.5.dev0"],
    tests_require=[],
    extras_require={},
    scripts=[],
    include_package_data=True,
    author="The INGInious authors",
    author_email="inginious@info.ucl.ac.be",
    license="AGPL 3",
    url="https://github.com/bastinjul/LEPL1402-IntelliJProjectGenerator"
)
