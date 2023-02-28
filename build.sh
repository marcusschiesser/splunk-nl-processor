#!/bin/bash
# install app's dependencies
python -m pip install -r nl-processor/requirements.txt -t nl-processor/lib
chmod 644 nl-processor/lib/charset_normalizer/*.so # otherwise app-inspect fails

# install build dependencies
python -m pip install -r nl-processor/requirements-dev.txt

# build docs
python -m markdown2 -x target-blank-links nl-processor/README > nl-processor/appserver/static/docs.html

# build package
python -m slim package nl-processor -o deploy -u error

# check package
/usr/local/python/current/bin/splunk-appinspect inspect ./deploy/nl-processor-*.tar.gz --mode test --generate-feedback  --output-file "deploy/AppInspect-results.json"