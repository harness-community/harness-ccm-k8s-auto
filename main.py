from os import getenv
from time import sleep

from requests import post, get, delete

PARAMS = {
    "accountIdentifier": getenv("HARNESS_ACCOUNT_ID"),
}

HEADERS = {
    "x-api-key": getenv("HARNESS_PLATFORM_API_KEY"),
}


def test_resp(resp):

    if resp.json().get("status") == "SUCCESS":
        print("SUCCESS")
    else:
        print(resp.text)


def get_delegates():

    return get(
        "https://app.harness.io/gateway/ng/api/delegate-token-ng/delegate-groups",
        params=PARAMS,
        headers=HEADERS,
    )


def get_connector(identifier: str):

    return get(
        f"https://app.harness.io/ng/api/connectors/{identifier}",
        params=PARAMS,
        headers=HEADERS,
    )


def delete_connector(identifier: str):

    return delete(
        f"https://app.harness.io/ng/api/connectors/{identifier}",
        params=PARAMS,
        headers=HEADERS,
    )


def create_k8s_connector(identifier: str, delegate_name: str):

    return post(
        "https://app.harness.io/gateway/ng/api/connectors",
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
                    # "connectorType": "KubernetesClusterConfig",
                    "credential": {"type": "InheritFromDelegate", "spec": None},
                    "delegateSelectors": [delegate_name],
                },
            }
        },
    )


def create_k8s_ccm_connector(identifier: str, k8s_connector: str):

    return post(
        "https://app.harness.io/gateway/ng/api/connectors",
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


if __name__ == "__main__":

    while True:

        resp = get_delegates()

        if resp.status_code != 200:
            print(f"error getting delegates: ", resp.text)

        for group in resp.json().get("resource", {}).get("delegateGroupDetails", []):

            identifier = group.get("delegateGroupIdentifier")
            name = group.get("groupName")

            resp = get_connector(identifier)

            if resp.status_code == 200:
                print("k8s connector exists for", identifier)

                if getenv("DELETE_CONNECTORS"):
                    print("deleting k8s connector for", identifier)
                    resp = delete_connector(identifier)
                    test_resp(resp)

            elif not getenv("DELETE_CONNECTORS"):
                print("need to create k8s connector for", identifier)
                resp = create_k8s_connector(identifier, name)
                test_resp(resp)

            resp = get_connector(identifier + "_ccm")

            if resp.status_code == 200:
                print("k8s ccm connector exists for", identifier)

                if getenv("DELETE_CONNECTORS"):
                    print("deleting k8s ccm connector for", identifier)
                    resp = delete_connector(identifier + "_ccm")
                    test_resp(resp)

            elif not getenv("DELETE_CONNECTORS"):
                print("need to create k8s ccm connector for", identifier)
                resp = create_k8s_ccm_connector(identifier + "_ccm", identifier)
                test_resp(resp)

        sleep(int(getenv("LOOP_SECODS", 60)))
