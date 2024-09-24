from setuptools import setup

with open("requirements.txt") as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name="Future Engineers 2025",
    version="0.0.1",
    packages=["src"],
    install_requires=REQUIREMENTS,
)