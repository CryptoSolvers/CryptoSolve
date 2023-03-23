from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name="symcollab-algebra",
    version="0.1.1",
    packages=find_namespace_packages(include=["symcollab.*"]),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/symcollab/cryptosolve",
    python_requires='>=3.8',
    install_requires = [
        "matplotlib~=3.6.2",
        "networkx~=2.8.8",
        "numpy~=1.23.5",
        "sympy==1.11.1",
        "pydot~=1.4.2"
    ]
)
