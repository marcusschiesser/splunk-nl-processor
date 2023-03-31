const appName = Splunk.util.getPath().match(`\/app\/(.+)\/.+`)[1];
require(["jquery", "splunkjs/splunk", "splunkjs/ready!"], function (
  $,
  splunkjs,
  _
) {
  const apiTokenInput = $("splunk-text-input[name='hf_api_token']");
  const openAIapiKeyInput = $("splunk-text-input[name='openai_api_key']");

  const http = new splunkjs.SplunkWebHttp();
  const service = new splunkjs.Service(http, {
    owner: "nobody",
    app: appName,
    sharing: "app",
  });

  const configure = async function () {
    return new Promise(function (resolve, reject) {
      const options = {
        hf_api_token: apiTokenInput.attr("value") || "",
        openai_api_key: openAIapiKeyInput.attr("value") || "",
      };
      const endpoint = new splunkjs.Service.Endpoint(service, "configure");
      endpoint.post("", options, function (err, response) {
        if (err) {
          console.log(err);
          reject(err);
          return;
        }
        resolve(response);
      });
    });
  };

  const performSetup = async function () {
    try {
      await configure();
    } catch (error) {
      alert("Error while configuring: " + error.error);
      return;
    }
    alert("Successfully configured the app.");
  };

  $("#setupButton").click(performSetup);
});
