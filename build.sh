#!/bin/bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r easy-ai/requirements.txt -t easy-ai/lib
python3 -m pip install -r easy-ai/requirements-dev.txt
