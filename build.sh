#!/bin/bash
python -m pip install -r nl-processor/requirements.txt -t nl-processor/lib
python -m pip install -r nl-processor/requirements-dev.txt
python -m markdown2 -x target-blank-links DOCS.md > nl-processor/appserver/static/docs.html