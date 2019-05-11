import threading

import factory
from django.conf import settings
from django.db.models.signals import post_save

from backend.models import UserInfo
from tests.utils import DEFAULT_USER


class Factory(factory.DjangoModelFactory):
    class Meta:
        strategy = factory.CREATE_STRATEGY
        model = None
        abstract = True

    _SEQUENCE = 1
    _SEQUENCE_LOCK = threading.Lock()

    @classmethod
    def _setup_next_sequence(cls):
        with cls._SEQUENCE_LOCK:
            cls._SEQUENCE += 1
        return cls._SEQUENCE


@factory.django.mute_signals(post_save)
class UserInfoFactory(factory.DjangoModelFactory):
    class Meta:
        model = UserInfo

    zip = DEFAULT_USER["userinfo"]["zip"]
    user = factory.SubFactory("tests.factories.UserFactory", userinfo=None)


@factory.django.mute_signals(post_save)
class UserFactory(Factory):
    class Meta:
        model = settings.AUTH_USER_MODEL
        strategy = factory.CREATE_STRATEGY

    first_name = DEFAULT_USER["first_name"]
    last_name = DEFAULT_USER["last_name"]
    username = factory.Sequence(lambda n: "user{}".format(n))
    email = factory.LazyAttribute(lambda obj: "%s@email.com" % obj.username)
    password = factory.PostGeneration(
        lambda obj, *args, **kwargs: obj.set_password(obj.username)
    )
    userinfo = factory.RelatedFactory(UserInfoFactory, "user")
