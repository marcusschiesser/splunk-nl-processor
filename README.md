# NLP Natural Language Processor

Splunk SPL Command to call AI Inference APIs for NLP for each event.

## Build

Run `bash build.sh`

## Run

1. Start Splunk: `docker-compose up`
2. Go to http://localhost:8000/en-US/app/nl_processor/search
3. Try the following example:

```
| makeresults
| eval payload="in München gibt es viele Unternehmen, z.b. BMW und Siemens."
| hflookup model="mschiesser/ner-bert-german" api_token="xxxx"
```

Get your `api_token` at http://hf.co/settings/tokens

## Docs

see [./nl_processor/README](./nl_processor/README)

## TODOs

1. Move `api_token` to encrypted conf file
2. Specify field to use for payload (currently it's `payload`).
3. Add more AI APIs, e.g. OpenAI API
