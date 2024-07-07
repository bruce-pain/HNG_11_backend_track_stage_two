from django.urls import path
from api_auth import views

urlpatterns = [
    path("register/", views.UserRegisterAPIView.as_view(), name="register"),
]
