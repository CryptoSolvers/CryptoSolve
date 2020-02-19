from setuptools import setup, find_packages

setup(name="theories",
    version="0.0.1",
    packages=find_packages(),
    install_requires = [
        # Our dependencies
        "algebra",
        "rewrite",
        # Outside dependencies
        "mypy>=0.740",
        "mypy-extensions>=0.4.0"
    ],
)
