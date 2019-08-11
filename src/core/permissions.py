from django.contrib.auth.models import Group
from rest_framework import permissions


def is_in_group(user, group_name):
    """
    Takes a user and a group name, returns `True` if the user is in that group
    """
    try:
        return Group.objects.get(name=group_name).user_set.filter(id=user.id).exists()
    except Group.DoesNotExist:
        return None


class HasGroupPermission(permissions.BasePermission):
    """
    Ensures user is either an admin or in the required groups
    """

    def has_permission(self, request, view):
        # Check if user is admin
        if bool(request.user and request.user.is_staff):
            return True

        # Get a mapping of methods -> required group
        required_groups_mapping = getattr(view, "required_groups", {})

        # Determine the required groups for this particular request method
        required_groups = required_groups_mapping.get(request.method, [])
        return all(
            [is_in_group(request.user, group_name) for group_name in required_groups]
        )
