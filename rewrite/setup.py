from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name="symcollab-rewrite",
    version="0.1.1",
    packages=find_namespace_packages(include=["symcollab.*"]),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/symcollab/cryptosolve",
    install_requires = [
        # Our dependencies
        "symcollab-algebra",
        "symcollab-unification",
        # Outside dependencies
        "mypy>=0.740",
        "mypy-extensions>=0.4.0"
    ],
)
