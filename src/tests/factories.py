import threading

import factory
from django.conf import settings
from django.db.models.signals import post_save

from core.models import Profile
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
class ProfileFactory(factory.DjangoModelFactory):
    class Meta:
        model = Profile

    zip = DEFAULT_USER["profile"]["zip"]
    user = factory.SubFactory("tests.factories.UserFactory", profile=None)


@factory.django.mute_signals(post_save)
class UserFactory(Factory):
    class Meta:
        model = settings.AUTH_USER_MODEL
        strategy = factory.CREATE_STRATEGY

    first_name = DEFAULT_USER["first_name"]
    last_name = DEFAULT_USER["last_name"]
    email = factory.Sequence(lambda n: f"user{n}@email.com")
    username = factory.LazyAttribute(lambda obj: obj.email)
    password = factory.PostGeneration(
        lambda obj, *args, **kwargs: obj.set_password(obj.username)
    )
    profile = factory.RelatedFactory(ProfileFactory, "user")
