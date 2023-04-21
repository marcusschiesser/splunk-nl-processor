# NLP Natural Language Processor

Splunk SPL Command to call AI Inference APIs for NLP for each event.

## Build

Make sure you run the project in the Dev container.

Run `bash build.sh`

## Run

1. Start Splunk: `docker-compose up`
2. Configure [API Token](http://hf.co/settings/tokens) at http://localhost:8000/en-US/app/nl_processor/setup
3. Go to http://localhost:8000/en-US/app/nl_processor/search

Then try one example from the [documentation](./nl_processor/README)

## TODOs

1. Specify field to use for payload (currently it's `payload`).
2. Add more AI APIs, e.g. OpenAI API
