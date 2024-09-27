#!/bin/bash
python3 -m build
echo "upload to pypi.org via:  twine upload dist/*"
