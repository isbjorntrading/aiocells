#!/bin/sh

set -e
set -u

export PYTHONPATH=src

pycodestyle --show-source --show-pep8 src
pycodestyle --show-source --show-pep8 tests
python -m pytest tests
