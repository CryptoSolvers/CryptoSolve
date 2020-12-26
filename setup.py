from setuptools import setup, find_packages

setup(name="symcollab",
    version="0.1.1",
    packages=find_packages(),
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
