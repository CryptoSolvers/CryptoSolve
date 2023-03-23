from setuptools import setup, find_namespace_packages
from glob import glob

# Add website files
data_files = []
directories = glob('symcollab/moe/website/partials/**/', recursive=True) + \
    glob('symcollab/moe/website/static/**/', recursive=True) + \
    glob('symcollab/moe/website/templates/**/', recursive=True)
for directory in directories:
    files = list(filter(lambda x: x + "/" not in directories, glob(directory + "*")))
    data_files.append((directory, files))

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name="symcollab-moe",
    version="0.1.3",
    packages=find_namespace_packages(include=["symcollab.*"]),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/symcollab/cryptosolve",
    scripts=["moo_tool", "moo_website"],
    python_requires='>=3.8',
    install_requires = [
        # Our dependencies
        "symcollab-algebra",
        "symcollab-unification",
        "symcollab-xor",
        # Outside dependencies
        "Flask~=2.2.2"
    ],
    data_files = data_files,
    include_package_data = True
)
