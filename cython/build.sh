#!/bin/bash
cd ..
cython --embed -o cython/st2cc.c st2cc/st2cc.py
cd cython
gcc -o st2cc st2cc.c $(python3-config --cflags) -L /opt/homebrew/opt/python@3.13/lib -lpython3.13 $(python3-config --ldflags)
