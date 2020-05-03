from django.urls import include, path
from rest_framework import routers

from api import views

router = routers.DefaultRouter()
router.register("codeschools", views.CodeSchoolViewSet)
router.register("locations", views.LocationViewSet)
router.register("scholarships", views.ScholarshipViewSet)
router.register("scholarshipApplications", views.ScholarshipApplicationViewSet)
router.register("teamMembers", views.TeamMemberViewSet)
router.register('sucessStory', views.SuccessStoryViewSet)

urlpatterns = [path("", include(router.urls))]
