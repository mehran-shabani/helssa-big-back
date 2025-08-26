import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestExampleEntityModel:
    def test_create_entity(self):
        from patient_chatbot.models import ExampleEntity

        entity = ExampleEntity.objects.create(name="Sample")
        assert entity.id is not None
        assert entity.created_at <= timezone.now()