#!/bin/bash
python -m pip install -r easy-ai/requirements.txt -t easy-ai/lib
python -m pip install -r easy-ai/requirements-dev.txt
python -m markdown2 -x target-blank-links DOCS.md > easy-ai/appserver/static/docs.html