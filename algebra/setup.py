from setuptools import setup, find_namespace_packages

setup(name="symcollab-algebra",
    version="0.1.1",
    packages=find_namespace_packages(include=["symcollab.*"]),
    install_requires = [
        "matplotlib~=3.1.1",
        "mypy~=0.740",
        "mypy-extensions~=0.4.0",
        "networkx~=2.3",
        "numpy~=1.17.0",
        "sympy==1.4",
    ]
)
