#!/bin/bash
# python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install ipykernel
python -m ipykernel install --user --name="$(basename "$PWD")" --display-name "Python ($(basename "$PWD"))"
