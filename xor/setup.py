from setuptools import setup, find_packages

setup(name="xor",
    version="0.0.1",
    packages=find_packages(),
    install_requires = [
        # Our dependencies
        "algebra"
    ],
)
