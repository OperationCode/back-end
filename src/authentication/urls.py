from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenVerifyView

from authentication import views

router = routers.DefaultRouter()

router.register("userinfo", views.UserInfoViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("token", views.CustomTokenObtainView.as_view(), name="token_obtain"),
    path("token/refresh", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify", TokenVerifyView.as_view(), name="token_verify"),
    path("register", views.create_user, name="register"),
    path("email/<str:email>", views.email_already_exists, name="check_email"),
    path("testAuthed", views.TestView.as_view(), name="authed"),
]
