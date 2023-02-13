#!/bin/bash
python -m pip install -r nl-processor/requirements.txt -t nl-processor/lib
python -m pip install -r nl-processor/requirements-dev.txt
python -m markdown2 -x target-blank-links DOCS.md > nl-processor/appserver/static/docs.html

# slim (installation needs to be --user otherwise permission errors since its setup will try to write to /usr/share)
python -m pip install --user splunk-packaging-toolkit==1.0.1 semantic_version==2.6.0
python -m slim package nl-processor -o deploy -u error

# run appinspect... needs to be in a venv because of dependency conflicts
# also needs libmagic installed (if not installed, execute the next two lines)
# sudo apt-get update -y
# sudo apt-get install -y libmagic-dev
python -m venv .appinspect
. ./.appinspect/bin/activate
pip install splunk-appinspect
splunk-appinspect inspect ./deploy/nl-processor-*.tar.gz
deactivate