from setuptools import setup, find_packages

setup(name="algebra",
    version="0.0.1",
    packages=find_packages(),
    install_requires = [
        "matplotlib>=3.1.1",
        "mypy>=0.740",
        "mypy-extensions>=0.4.0",
        "networkx>=2.3",
        "numpy>=1.17.0"
        "sympy>=1.4"
    ]
)
