#!/bin/bash
# clean up 
rm nl_processor/app.manifest
rm -fr deploy

# install app's dependencies
python -m pip install -r nl_processor/requirements.txt -t nl_processor/lib
# fix app-inspect fails
find nl_processor/lib -type f -exec chmod 644 {} \;

# install build dependencies
python -m pip install -r nl_processor/requirements-dev.txt

# build docs
python -m markdown2 -x target-blank-links nl_processor/README > nl_processor/appserver/static/docs.html

# build package
python -m slim package nl_processor -o deploy -u error

# check package
splunk-appinspect inspect ./deploy/nl_processor-*.tar.gz --mode test --generate-feedback  --output-file "deploy/AppInspect-results.json"