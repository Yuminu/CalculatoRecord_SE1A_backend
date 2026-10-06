"""API-level tests for the calculator backend."""

import pytest

from app import create_app


@pytest.fixture()
def app():
    """Create an application bound to an in-memory database."""
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )
    yield application


@pytest.fixture()
def client(app):
    """Return a Flask test client for the application."""
    return app.test_client()


def test_health_check(client):
    """GET /api/health returns the running status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["message"] == "Calculator API is running"


def test_calculate_success(client):
    """POST /api/calculate returns the full success contract."""
    response = client.post(
        "/api/calculate", json={"expression": "(1+2)*3"}
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["expression"] == "(1+2)*3"
    assert payload["result"] == 9
    assert payload["message"] == "Calculation successful"
    assert "timestamp" in payload


def test_calculate_invalid_expression(client):
    """POST /api/calculate rejects an illegal expression with HTTP 400."""
    response = client.post("/api/calculate", json={"expression": "1++2"})
    assert response.status_code == 400
    payload = response.get_json()
    assert payload["success"] is False
    assert payload["message"]


def test_calculate_missing_expression(client):
    """POST /api/calculate without an expression returns HTTP 400."""
    response = client.post("/api/calculate", json={})
    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_calculate_division_by_zero(client):
    """POST /api/calculate reports division by zero with HTTP 400."""
    response = client.post("/api/calculate", json={"expression": "1/0"})
    assert response.status_code == 400
    assert response.get_json()["message"] == "Division by zero"


def test_history_after_calculation(client):
    """A calculation is persisted and returned by GET /api/history."""
    client.post("/api/calculate", json={"expression": "1+1"})
    response = client.get("/api/history")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["total"] == 1
    assert payload["data"][0]["expression"] == "1+1"
    assert payload["data"][0]["result"] == 2
    assert payload["data"][0]["is_favorite"] is False


def test_delete_single_history(client):
    """DELETE /api/history/{id} removes a record and returns HTTP 204."""
    client.post("/api/calculate", json={"expression": "2+2"})
    record_id = client.get("/api/history").get_json()["data"][0]["id"]
    response = client.delete("/api/history/{}".format(record_id))
    assert response.status_code == 204
    assert client.get("/api/history").get_json()["total"] == 0


def test_delete_missing_history_returns_404(client):
    """DELETE /api/history/{id} returns HTTP 404 for an unknown id."""
    response = client.delete("/api/history/999999")
    assert response.status_code == 404
    payload = response.get_json()
    assert payload["message"] == "History record not found"


def test_clear_all_history(client):
    """DELETE /api/history clears everything and returns HTTP 204."""
    client.post("/api/calculate", json={"expression": "3+3"})
    response = client.delete("/api/history")
    assert response.status_code == 204
    assert client.get("/api/history").get_json()["total"] == 0


def test_default_history_limit_is_100(app):
    """The configured history cap defaults to 100 records."""
    assert app.config["MAX_HISTORY_RECORDS"] == 100


def test_history_limit_trims_oldest(app, client):
    """The oldest records are removed once the cap is exceeded."""
    app.config["MAX_HISTORY_RECORDS"] = 3
    for index in range(5):
        client.post(
            "/api/calculate", json={"expression": "1+{}".format(index)}
        )
    payload = client.get(
        "/api/history", query_string={"limit": 100}
    ).get_json()
    assert payload["total"] == 3
    expressions = [item["expression"] for item in payload["data"]]
    assert "1+0" not in expressions
    assert "1+4" in expressions


def test_toggle_favorite(client):
    """PATCH /api/history/{id}/favorite flips the favorite flag."""
    client.post("/api/calculate", json={"expression": "4+4"})
    record_id = client.get("/api/history").get_json()["data"][0]["id"]

    response = client.patch(
        "/api/history/{}/favorite".format(record_id)
    )
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["is_favorite"] is True

    response = client.patch(
        "/api/history/{}/favorite".format(record_id)
    )
    assert response.get_json()["is_favorite"] is False


def test_toggle_favorite_missing_returns_404(client):
    """Toggling a favorite on an unknown id returns HTTP 404."""
    response = client.patch("/api/history/999999/favorite")
    assert response.status_code == 404
    assert response.get_json()["success"] is False


def test_history_filter_favorite(client):
    """GET /api/history?favorite=true only returns favorite records."""
    client.post("/api/calculate", json={"expression": "1+1"})
    client.post("/api/calculate", json={"expression": "2+2"})
    data = client.get("/api/history").get_json()["data"]
    favorite_id = data[0]["id"]
    other_id = data[1]["id"]
    client.patch("/api/history/{}/favorite".format(favorite_id))

    payload = client.get(
        "/api/history", query_string={"favorite": "true"}
    ).get_json()
    assert payload["total"] == 1
    assert payload["data"][0]["id"] == favorite_id
    assert payload["data"][0]["is_favorite"] is True
    assert payload["data"][0]["id"] != other_id
