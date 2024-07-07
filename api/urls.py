from django.urls import path

from api import views

urlpatterns = [
    path("users/<uuid:userId>", views.UserDetailAPIView.as_view(), name="user-detail"),
    path("organisations/", views.OrganisationAPIView.as_view(), name="organisations"),
    path(
        "organisations/<uuid:orgId>",
        views.OrganisationDetailAPIView.as_view(),
        name="organisation-detail",
    ),
]
