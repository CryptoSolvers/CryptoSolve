#!/usr/bin/env sh

setup_package () {
  cd $1 && pip install --editable . ; cd ..
}

# First uninstall any installed packages
pip uninstall algebra
pip uninstall xor
pip uninstall theories
pip uninstall Unification
pip uninstall rewrite
pip uninstall moe

# Then setup the packages to mirror the local repo
setup_package algebra
setup_package xor
setup_package theories
setup_package Unification
setup_package rewrite
setup_package moe

# Developer utilities
pip install sphinx tox pylint
