from os import getenv
from sys import exit
from time import sleep
from logging import getLogger, debug, info, warning, error

from requests import post, get, delete


getLogger().setLevel(level=getenv("PLUGIN_LOG_LEVEL", "INFO").upper())

PARAMS = {
    "accountIdentifier": getenv("PLUGIN_HARNESS_ACCOUNT_ID"),
}

HEADERS = {
    "x-api-key": getenv("PLUGIN_HARNESS_PLATFORM_API_KEY"),
}

HARNESS_ENDPOINT = getenv("PLUGIN_HARNESS_ENDPOINT", "https://app.harness.io")


def get_delegates() -> list:
    resp = get(
        f"{HARNESS_ENDPOINT}/gateway/ng/api/delegate-token-ng/delegate-groups",
        params=PARAMS,
        headers=HEADERS,
    )

    if resp.status_code != 200:
        error(f"error getting delegates: {resp.text}")
        return []

    return resp.json().get("resource", {}).get("delegateGroupDetails", [])


def get_connector(identifier: str) -> dict:
    resp = get(
        f"{HARNESS_ENDPOINT}/ng/api/connectors/{identifier}",
        params=PARAMS,
        headers=HEADERS,
    )

    if (
        resp.status_code != 200
        and resp.json().get("code") != "RESOURCE_NOT_FOUND_EXCEPTION"
    ):
        error(f"error getting connector: {resp.text}")
        return {}

    if resp.json().get("code") == "RESOURCE_NOT_FOUND_EXCEPTION":
        return {}

    return resp.json()


def delete_connector(identifier: str) -> dict:
    resp = delete(
        f"{HARNESS_ENDPOINT}/ng/api/connectors/{identifier}",
        params=PARAMS,
        headers=HEADERS,
    )

    if resp.status_code != 200 and "No such" not in resp.json().get("message"):
        error(f"error deleting connector: {resp.text}")
        return {}

    return resp.json()


def create_k8s_connector(identifier: str, delegate_name: str) -> dict:
    resp = post(
        f"{HARNESS_ENDPOINT}/gateway/ng/api/connectors",
        params=PARAMS,
        headers=HEADERS,
        json={
            "connector": {
                "name": delegate_name,
                "identifier": identifier,
                "description": "created via automation",
                "tags": {},
                "type": "K8sCluster",
                "spec": {
                    "credential": {"type": "InheritFromDelegate", "spec": None},
                    "delegateSelectors": [delegate_name],
                },
            }
        },
    )

    if resp.status_code != 200:
        error("error creating connector: {resp.text}")
        return {}

    return resp.json()


def create_k8s_ccm_connector(identifier: str, k8s_connector: str) -> dict:
    resp = post(
        f"{HARNESS_ENDPOINT}/gateway/ng/api/connectors",
        params=PARAMS,
        headers=HEADERS,
        json={
            "connector": {
                "name": identifier,
                "identifier": identifier,
                "description": "created via automation",
                "type": "CEK8sCluster",
                "spec": {
                    "connectorType": "CEKubernetesClusterConfigDTO",
                    "featuresEnabled": ["VISIBILITY"],
                    "connectorRef": k8s_connector,
                },
            }
        },
    )

    if resp.status_code != 200:
        error(f"error creating connector: {resp.text}")
        return {}

    return resp.json()


def main(
    sleepsec: int, oneshot: bool, connector_prefix: str = "", delete: bool = False
):
    while True:
        for delegate in get_delegates():
            identifier = connector_prefix + delegate.get("delegateGroupIdentifier")
            name = delegate.get("groupName")

            if get_connector(identifier):
                debug(f"k8s connector exists for {identifier}")

                if delete:
                    info(f"deleting k8s connector for {identifier}")
                    delete_connector(identifier)

            elif not delete:
                info(f"creating k8s connector for {identifier}")
                create_k8s_connector(identifier, name)

            if get_connector(identifier + "_ccm"):
                debug(f"k8s ccm connector exists for {identifier}")

                if delete:
                    info(f"deleting k8s ccm connector for {identifier}")
                    delete_connector(identifier + "_ccm")

            elif not delete:
                info(f"creating k8s ccm connector for {identifier}")
                create_k8s_ccm_connector(identifier + "_ccm", identifier)

        if oneshot:
            exit(0)

        info(f"sleeping for {sleepsec}")
        sleep(sleepsec)


if __name__ == "__main__":
    main(
        int(getenv("PLUGIN_LOOP_SECONDS", 60)),
        getenv("PLUGIN_ONESHOT"),
        getenv("PLUGIN_CONNECTOR_PREFIX", ""),
        getenv("PLUGIN_DELETE_CONNECTORS"),
    )
