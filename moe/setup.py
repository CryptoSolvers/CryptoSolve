from setuptools import setup, find_namespace_packages
from glob import glob

# Add website files
data_files = []
directories = glob('moe/website/partials/**/', recursive=True) + \
    glob('moe/website/static/**/', recursive=True) + \
    glob('moe/website/templates/**/', recursive=True)
for directory in directories:
    files = list(filter(lambda x: x + "/" not in directories, glob(directory + "*")))
    data_files.append((directory, files))


setup(name="symcollab-moe",
    version="0.1.1",
    packages=find_namespace_packages(include=["symcollab.*"]),
    scripts=["moe_tool", "moe_website"],
    install_requires = [
        # Our dependencies
        "symcollab-algebra",
        "symcollab-unification",
        "symcollab-xor",
        # Outside dependencies
        "Flask>=1.1.1",
        "mypy>=0.740",
        "mypy-extensions>=0.4.0",
    ],
    data_files = data_files,
    include_package_data = True
)
