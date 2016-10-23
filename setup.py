from setuptools import setup, find_packages

setup(
    name="nomad",
    version="0.2",
    packages=find_packages(),
    install_requires=['pyyaml', 'pylxd'],
    entry_points={
        'console_scripts': [
            'nomad = nomad:main',
        ],
    },
)
