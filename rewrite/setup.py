from setuptools import setup, find_namespace_packages

setup(name="symcollab-rewrite",
    version="0.1.1",
    packages=find_namespace_packages(include=["symcollab.*"]),
    install_requires = [
        # Our dependencies
        "symcollab-algebra",
        "symcollab-unification",
        # Outside dependencies
        "mypy>=0.740",
        "mypy-extensions>=0.4.0"
    ],
)
