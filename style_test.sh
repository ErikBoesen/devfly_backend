#!/usr/bin/env bash
# E501 Line too long
# E402 Import not at top of file
# E265 block comment should start with '# '
# W503 Line break occurred before a binary operator
# E711 comparison to None should be 'if cond is None:'
pycodestyle *.py app/*.py --ignore=E501,E402,E265,W503,E711
