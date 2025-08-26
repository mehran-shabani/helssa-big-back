import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestIntegration:
    def test_entity_crud_flow(self, client, django_user_model):
        # Health
        url = reverse("soapify-health")
        assert client.get(url).status_code == 200

        # Auth required endpoints will be 403/401 in this minimal template
        list_url = reverse("soapify-entities")
        assert client.get(list_url).status_code in (401, 403)