from setuptools import setup
import os


def read_requirements(filename: str) -> list:
    return open(os.path.join(os.path.dirname(__file__), filename)).read().split("\n")


setup(
    name="ego",
    author="Yotam Manor",
    description="",
    version="1.0.0",
    packages=['src'],
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        'console_scripts': [
            'ego = src.ego:main'
        ]
    }
)
