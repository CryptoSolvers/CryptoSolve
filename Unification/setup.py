from setuptools import setup, find_packages

setup(name="Unification",
    version="0.1",
    packages=find_packages(),
    install_requires = [
        # Our own projects
        "algebra",
        "xor",
        # Outside dependencies
        "mypy~=0.740",
        "mypy-extensions~=0.4.0",
        "scipy~=1.3.1",
        "sympy==1.4"
    ],
)
