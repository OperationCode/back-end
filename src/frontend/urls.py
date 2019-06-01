from django.urls import path

from . import views

urlpatterns = [
    path("forms/codeschool", views.CodeschoolFormView.as_view(), name="codeschool_form")
]
