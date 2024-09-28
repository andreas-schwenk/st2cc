#!/bin/bash

# Displays all files in this repository that are currently being ignored by Git 
# according to the .gitignore configuration.
git ls-files --others --ignored --exclude-standard
