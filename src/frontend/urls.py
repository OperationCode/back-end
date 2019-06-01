from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index_view"),
    path(
        "forms/codeschool", views.CodeschoolFormView.as_view(), name="codeschool_form"
    ),
]
