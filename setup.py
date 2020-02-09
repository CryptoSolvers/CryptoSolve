from setuptools import setup, find_packages
from glob import glob

# Add website files
data_files = []
directories = glob('moe/website/partials/**/', recursive=True) + \
    glob('moe/website/static/**/', recursive=True) + \
    glob('moe/website/templates/**/', recursive=True)
for directory in directories:
    files = list(filter(lambda x: x + "/" not in directories, glob(directory + "*")))
    data_files.append((directory, files))


setup(name="moe",
    version="0.0.1",
    packages=find_packages(),
    scripts=["moe/moe_tool", "view_notebook", "moe/moe_website"],
    install_requires = [
        "Flask>=1.1.1",
        "matplotlib>=3.1.1",
        "mypy>=0.740",
        "mypy-extensions>=0.4.0",
        "networkx>=2.3",
        "notebook>=6.0.0",
        "jupyterlab>=1.2.0",
        "jupyter-client>=5.3.0",
        "numpy>=1.17.0"
        "scipy>=1.3.1",
        "sympy>=1.4"
    ],
    data_files = data_files,
    include_package_data = True
)