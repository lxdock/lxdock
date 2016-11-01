# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup

import nomad

setup(
    name='nomad',
    version=nomad.__version__,
    packages=find_packages(),
    install_requires=[
        'pylxd',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'nomad = nomad.cli.main:main',
        ],
    },
)
