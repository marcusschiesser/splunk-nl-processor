# Easy AI

Splunk SPL Command to call AI Inference APIs for each event.

## Build

Run `bash build.sh`

## Run

1. Start Splunk: `docker-compose up --build`
2. Go to http://localhost:8000/en-US/app/easy-ai/search
3. Try the following example:

```
| makeresults \
| eval payload="in münchen gibt es viele unternehmen, z.b. bmw und siemens."\
| ailookup model="mschiesser/ner-bert-german" api_token="xxxx"
```

Get your `api_token` at hf.co/settings/tokens

## Docs

see [searchbnf.conf](./easy-ai/default/searchbnf.conf)

## TODOs

1. Move `api_token` to encrypted conf file
2. Specify field to use for payload (currently it's `payload`).
3. Add more AI APIs, e.g. OpenAI API
