from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name="symcollab",
    version="0.1.1",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/symcollab/cryptosolve",
    install_requires = [
        "symcollab-algebra",
        "symcollab-xor",
        "symcollab-unification",
        "symcollab-rewrite",
        "symcollab-theories",
        "symcollab-moe"
    ]
)
