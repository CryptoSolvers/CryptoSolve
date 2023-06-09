#!/usr/bin/env sh

if ! python3 -c 'import sys; assert sys.version_info >= (3,8)' 2> /dev/null; then
	echo "Requires Python version greater than 3.8"
	exit 1
fi

setup_package () {
  cd $1 && pip install --editable . ; cd ..
}

# First uninstall any installed packages
pip uninstall symcollab-algebra
pip uninstall symcollab-xor
pip uninstall symcollab-theories
pip uninstall symcollab-unification
pip uninstall symcollab-rewrite
pip uninstall symcollab-moe
pip uninstall symcollab

# Then setup the packages to mirror the local repo
setup_package algebra
setup_package xor
setup_package Unification
setup_package rewrite
setup_package theories
setup_package moe

# Developer utilities
pip install sphinx tox pylint
