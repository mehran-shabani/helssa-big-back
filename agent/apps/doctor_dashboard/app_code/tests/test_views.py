import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestViews:
    def test_health_ok(self, client):
        url = reverse("doctor_dashboard-health")
        response = client.get(url)
        assert response.status_code == 200
        assert response.json()["status"] == "ok"