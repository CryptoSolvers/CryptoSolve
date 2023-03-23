#!/usr/bin/env sh

if ! python3 -c 'import sys; assert sys.version_info >= (3,8)' 2> /dev/null; then
        echo "Requires Python version greater than 3.8"
        exit 1
fi


pip install algebra/
pip install xor/
pip install Unification/
pip install rewrite/
pip install theories/
pip install moe/

