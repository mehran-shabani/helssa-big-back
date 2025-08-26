from rest_framework import serializers
from .models import ExampleEntity


class ExampleEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleEntity
        fields = ["id", "name", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]