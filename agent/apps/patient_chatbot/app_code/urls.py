from django.urls import path
from . import views


urlpatterns = [
    path("health/", views.health, name="patient_chatbot-health"),
    path("entities/", views.ExampleEntityListCreateView.as_view(), name="patient_chatbot-entities"),
    path("entities/<int:pk>/", views.ExampleEntityRetrieveUpdateDestroyView.as_view(), name="patient_chatbot-entity-detail"),
]