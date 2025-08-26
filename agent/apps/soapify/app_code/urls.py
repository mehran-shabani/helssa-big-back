from django.urls import path
from . import views


urlpatterns = [
    path("health/", views.health, name="soapify-health"),
    path("entities/", views.ExampleEntityListCreateView.as_view(), name="soapify-entities"),
    path("entities/<int:pk>/", views.ExampleEntityRetrieveUpdateDestroyView.as_view(), name="soapify-entity-detail"),
]