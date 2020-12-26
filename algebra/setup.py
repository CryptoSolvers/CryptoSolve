from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name="symcollab-algebra",
    version="0.1.1",
    packages=find_namespace_packages(include=["symcollab.*"]),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/symcollab/cryptosolve",
    install_requires = [
        "matplotlib~=3.1.1",
        "mypy~=0.740",
        "mypy-extensions~=0.4.0",
        "networkx~=2.3",
        "numpy~=1.17.0",
        "sympy==1.4",
    ]
)
