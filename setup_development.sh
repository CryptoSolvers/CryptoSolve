#!/usr/bin/env sh

setup_package () {
  cd $1 && python setup.py develop ; cd ..
}

setup_package algebra
setup_package xor
setup_package theories
setup_package Unification
setup_package rewrite
setup_package moe
