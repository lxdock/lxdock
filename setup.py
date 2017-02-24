import sys

from setuptools import find_packages
from setuptools import setup

import lxdock

if sys.version_info < (3, 4):
    sys.exit('lxdock requires Python 3.4+ to run')

setup(
    name='lxdock',
    version=lxdock.__version__,
    author='Virgil Dupras, Morgan Aubert',
    author_email='',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/lxdock/lxdock',
    license='GPLv3',
    description='LXDock is a tool for orchestrating LXD containers.',
    keywords='lxd lxc containers environments orchestration devops',
    zip_safe=False,
    install_requires=[
        'colorlog>=2.0,<3.0',
        'pylxd>=2.2,<3.0',
        'PyYAML>=3.0,<4.0',
        'voluptuous>=0.9,<1.0',
    ],
    tests_require=[
        'pytest',
    ],
    entry_points={
        'console_scripts': [
            'lxdock = lxdock.cli.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
