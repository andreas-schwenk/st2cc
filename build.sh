#!/bin/bash
mkdir -p dist/
rm -rf dist/*.whl
rm -rf dist/*.tar.gz
python3 -m build
echo "upload to pypi.org via:  twine upload dist/*"
