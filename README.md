# harness-ccm-k8s-auto

automatically create k8s and k8s-ccm connectors for new delegates in your account

# usage

## auth

HARNESS_ACCOUNT_ID: harness account id

HARNESS_PLATFORM_API_KEY: harness api key, requires delegate:read and connectors:read/writ

## settings

LOOP_SECODS: number of seconds between checks (default: 60)

DELETE_CONNECTORS: if set (to anything) delete the connectors

## docker

build: `docker build -t harness-ccm-k8s-auto .`

run: `docker run -e HARNESS_ACCOUNT_ID=$HARNESS_ACCOUNT_ID -e HARNESS_PLATFORM_API_KEY=$HARNESS_PLATFORM_API_KEY --rm -it harness-ccm-k8s-auto`

## python

install: `pip install -r requirements.txt`

run: `python main.py`
