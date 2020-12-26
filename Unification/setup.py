from setuptools import setup, find_namespace_packages

setup(name="symcollab-unification",
    version="0.1.1",
    packages=find_namespace_packages(include=["symcollab.*"]),
    url="https://github.com/symcollab/cryptosolve",
    install_requires = [
        # Our own projects
        "symcollab-algebra",
        "symcollab-xor",
        # Outside dependencies
        "mypy~=0.740",
        "mypy-extensions~=0.4.0",
        "scipy~=1.5.4",
        "sympy==1.4"
    ],
)
