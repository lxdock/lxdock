from setuptools import setup, find_packages

setup(
    name="vith",
    version="0.1",
    packages=find_packages(),
    install_requires=['pyyaml'],
    entry_points={
        'console_scripts': [
            'vith = vith:main',
        ],
    },
)
