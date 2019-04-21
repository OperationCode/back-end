from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenVerifyView

from api import views

router = routers.DefaultRouter()
router.register("codeschools", views.CodeSchoolViewSet)
router.register("locations", views.LocationViewSet)
router.register("resources", views.ResourceViewSet)
router.register("scholarships", views.ScholarshipViewSet)
router.register("scholarshipApplications", views.ScholarshipApplicationViewSet)
router.register("teamMembers", views.TeamMemberViewSet)
router.register("userinfos", views.UserInfoViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("token", views.CustomTokenObtainView.as_view(), name="token_obtain_pair"),
    path("token/refresh", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify", TokenVerifyView.as_view(), name="token_verify"),
    path("register", views.create_user, name="register"),
    path("authed", views.TestView.as_view(), name="authed"),
]
