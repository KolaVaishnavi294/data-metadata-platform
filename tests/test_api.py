import requests

BASE_URL = "http://localhost:5000"

def test_search_endpoint():
    print("Testing search endpoint...")

    res = requests.get(f"{BASE_URL}/search?q=openfood")

    assert res.status_code == 200

    print("Search endpoint working")


def test_lineage_endpoint():
    print("Testing lineage endpoint...")

    res = requests.get(f"{BASE_URL}/datasets/test/lineage")

    assert res.status_code in [200, 404]

    print("Lineage endpoint reachable")


def test_openlineage_endpoint():
    print("Testing OpenLineage event endpoint...")

    payload = {
        "eventType": "TEST",
        "job": {
            "namespace": "test",
            "name": "test_job"
        },
        "inputs": [{"name": "input_dataset"}],
        "outputs": [{"name": "output_dataset"}]
    }

    res = requests.post(
        f"{BASE_URL}/openlineage/events",
        json=payload
    )

    assert res.status_code == 200

    print("OpenLineage endpoint working")


if __name__ == "__main__":
    test_search_endpoint()
    test_lineage_endpoint()
    test_openlineage_endpoint()

    print("All API tests passed successfully")