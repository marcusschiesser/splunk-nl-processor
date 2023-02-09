# About

Splunk SPL command to call AI Inference APIs for each event.
Currently, only the Inference API from [Hugging Face](https://huggingface.co/) is supported. 
Hugging face contains all different kinds of AI models - for Splunk use cases mostly the [Natural Language Processing models](https://huggingface.co/models) (e.g. Text Classification) are of interest. 
For example, it's possible to detect malicious domain names with text classification.

# Usage

The `ailookup` command runs the [Hugging Face AI Inference API](https://huggingface.co/inference-api) for each input event by passing the event's `payload` parameter and returns a new event for each result of the API call.

The parameter `model` specifies the ID of the [Hugging Face model](https://huggingface.co/models) to use, e.g. [`mschiesser/ner-bert-german`](https://huggingface.co/mschiesser/ner-bert-german).
Pass the [API token for the Hugging Face API](http://hf.co/settings/tokens) as parameter `api_token`.
If you want to limit the amount of API calls, you can specify a maximum number of calls with the parameter `maxcalls`.
If you want to continue on errors, you can specify the parameter `continue_on_errors=true`.

# Examples

Before running any of the examples, please make sure to get an [API token from Hugging Face](http://hf.co/settings/tokens) and use it in the `api_token` parameter.

Note that some models in Hugging Face are not often used and therefore loaded on-demand. If you're getting a `Model ... is currently loading` error, please try again after half a minute.

## Named Entity Recognition

The following example is using [named-entity recognition](https://en.wikipedia.org/wiki/Named-entity_recognition), to extract the location, names, and organizations of the string given as `payload`: 

    | makeresults
    | eval payload="My name is Clara and I live in San Jose, California and I am working there for Splunk."
    | ailookup model="Jean-Baptiste/roberta-large-ner-english" api_token="xxxx"

You can also try another model, to do named-entity recognition in German:

    | makeresults
    | eval payload="in münchen gibt es viele unternehmen, z.b. bmw und siemens."
    | ailookup model="mschiesser/ner-bert-german" api_token="xxxx"

## Sentiment Analysis

The following example is using [Sentiment analysis](https://en.wikipedia.org/wiki/Sentiment_analysis), to extract the sentiment of the sentence given as `payload`: 

    | makeresults
    | eval payload="Covid cases are increasing fast!"
    | ailookup model="cardiffnlp/twitter-roberta-base-sentiment-latest" api_token="xxxx"

# Contact

To run the command in production, you might want to:

1. Cache the results to limit the number of API calls
2. Run the inference in your own cloud or data center for security reasons
3. Train new AI models fitting the needs of your use cases
4. Set up a [MLOps](https://en.wikipedia.org/wiki/MLOps) pipeline for Splunk to update your AI models during run-time.

Feel free to [contact me](mailto:mail@marcusschiesser.de) for any of these problems. My team and I are glad to help.