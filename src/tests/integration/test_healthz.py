import pytest
from django import test


@pytest.mark.django_db
def test_healthz_reports_database_ok():
    res = test.Client().get("/healthz", {"format": "json"})

    assert res.status_code == 200
    assert res.json() == {"Database(alias='default')": "OK"}
