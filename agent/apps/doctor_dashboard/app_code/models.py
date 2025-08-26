from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model with created/updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ExampleEntity(TimeStampedModel):
    """Replace with domain models derived from PLAN.md."""
    name = models.CharField(max_length=255)
    owner_id = models.UUIDField(null=True, blank=True, help_text="User ID of the creator")

    def __str__(self) -> str:
        return self.name