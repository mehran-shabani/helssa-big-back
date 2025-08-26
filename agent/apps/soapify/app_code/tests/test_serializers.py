import pytest


@pytest.mark.django_db
class TestSerializers:
    def test_example_entity_serializer(self):
        from soapify.serializers import ExampleEntitySerializer

        serializer = ExampleEntitySerializer(data={"name": "Sample"})
        assert serializer.is_valid(), serializer.errors