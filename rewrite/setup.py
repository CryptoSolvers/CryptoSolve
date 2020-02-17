from setuptools import setup, find_packages

setup(name="rewrite",
    version="0.0.1",
    packages=find_packages(),
    install_requires = [
        # Our dependencies
        "algebra",
        "Unification",
        # Outside dependencies
        "mypy>=0.740",
        "mypy-extensions>=0.4.0"
    ],
)
