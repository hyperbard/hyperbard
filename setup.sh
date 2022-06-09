#!/bin/sh
#
# Create virtual environment or executes `poetry` installation,
# depending on the choice of the user.
#
# Usage:
#
#   ./setup.sh poetry   # For poetry installation
#   ./setup.sh venv     # For venv installation

SETUP=${1:-poetry}

if [ "${SETUP}" = poetry ]; then
  echo "Running poetry installation"
  poetry install
  poetry shell
fi

if [[ "${SETUP}" = venv ]]; then
  echo "Running venv installation"
	python3 -m venv .venv
	. .venv/bin/activate
	python3 -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .
fi
