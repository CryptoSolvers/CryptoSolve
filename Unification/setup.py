from setuptools import setup, find_namespace_packages

setup(name="symcollab-unification",
    version="0.1.1",
    packages=find_namespace_packages(include=["symcollab.*"]),
    url="https://github.com/symcollab/cryptosolve",
    python_requires='>=3.8',
    install_requires = [
        # Our own projects
        "symcollab-algebra",
        "symcollab-xor",
        # Outside dependencies
        "scipy~=1.9.3",
        "sympy~=1.11.1",
        "z3-solver~=4.11.2.0"
    ],
)
