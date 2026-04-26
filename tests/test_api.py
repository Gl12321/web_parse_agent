import requests

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"


def test_health():
    response = requests.get(f"{BASE_URL}/docs", timeout=5)
    assert response.status_code == 200
    print("PASS: API is alive (/docs accessible)")


def test_result_not_found():
    response = requests.get(
        f"{API_URL}/result",
        params={"schema_key": "contact", "url": "https://nonexistent.com"},
        timeout=5
    )
    assert response.status_code == 404
    print("PASS: Returns 404 for missing data")


if __name__ == "__main__":
    test_health()
    test_result_not_found()
    print("\nAll tests passed")
