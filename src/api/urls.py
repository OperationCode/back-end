from django.urls import include, path
from rest_framework import routers

from api import views

router = routers.DefaultRouter()
router.register("codeschools", views.CodeSchoolViewSet)
router.register("locations", views.LocationViewSet)
router.register("resources", views.ResourceViewSet)
router.register("scholarships", views.ScholarshipViewSet)
router.register("scholarshipApplications", views.ScholarshipApplicationViewSet)
router.register("teamMembers", views.TeamMemberViewSet)
router.register("events", views.EventViewSet)
router.register("gitHubStatistics", views.GitHubStatisticViewSet)
router.register("gitHubUsers", views.GitHubUserViewSet)
router.register("requests", views.RequestViewSet)
router.register("services", views.ServiceViewSet)
router.register("tags", views.TagViewSet)
router.register("votes", views.VoteViewSet)

urlpatterns = [path("", include(router.urls))]
