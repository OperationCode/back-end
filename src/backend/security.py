from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User as AuthUser

from authentication.models import User


class CustomBackend:
    @staticmethod
    def authenticate(request, username=None, password=None):
        user = User.objects.get(email=username)
        if not user:
            return None

        formatted_password = f"bcrypt${user.encrypted_password}"

        pwd_valid = check_password(password, formatted_password)
        if pwd_valid:
            try:
                user = AuthUser.objects.get(email=username)
            except AuthUser.DoesNotExist:
                user = AuthUser(
                    username=username, password=formatted_password, email=username
                )
                user.is_staff = True
                user.is_superuser = True
                user.save()
            return user
        return None

    @staticmethod
    def get_user(user_id):
        try:
            return AuthUser.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
