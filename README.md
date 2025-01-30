# harness-ccm-k8s-auto

automatically create k8s and k8s-ccm connectors for new delegates in your account

# usage

## auth

`PLUGIN_HARNESS_ACCOUNT_ID`: harness account id

`PLUGIN_HARNESS_PLATFORM_API_KEY`: harness api key, requires delegate:read and connectors:read/write

## settings

`PLUGIN_HARNESS_ENDPOINT`: base URL for the Harness API (default: https://app.harness.io)

`PLUGIN_CONNECTOR_PREFIX`: prefix to be added to connector identifiers (default: None)

`PLUGIN_LOOP_SECODS`: number of seconds between checks (default: 60)

`PLUGIN_DELETE_CONNECTORS`: if set (to anything) delete the connectors

`PLUGIN_ONESHOT`: do not loop, execute once and quit

`PLUGIN_LOG_LEVEL`: debug, info, warning, error

## docker

build: `docker build -t harness-ccm-k8s-auto .`

run: `docker run -e HARNESS_ACCOUNT_ID=$HARNESS_ACCOUNT_ID -e HARNESS_PLATFORM_API_KEY=$HARNESS_PLATFORM_API_KEY --rm -it harness-ccm-k8s-auto`

## python

install: `pip install -r requirements.txt`

run: `python main.py`

## master url and sa

spec for a connector using master url:
```
{
    "credential": {
        "type": "ManualConfig",
        "spec": {
            "masterUrl": "https://sdfdsfsdf.com:6443",
            "auth": {
                "type": "ServiceAccount",
                "spec": {
                    "serviceAccountTokenRef": "account.lab_ccm_sa_token",
                    "caCertRef": null
                }
            }
        }
    },
    "delegateSelectors": []
}
```
