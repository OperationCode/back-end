import threading

# import factory
from factory import (
    DjangoModelFactory,
    CREATE_STRATEGY,
    LazyAttribute,
    LazyFunction,
    django,
    SubFactory,
    PostGeneration,
    RelatedFactory,
)
from allauth.account.models import EmailAddress
from django.conf import settings
from django.db.models.signals import post_save

from core.models import Profile
from tests.test_data import (
    fake,
    DEFAULT_PASSWORD,
    random_branch,
    random_pay_grade,
    random_mos,
)


class Factory(DjangoModelFactory):
    class Meta:
        strategy = CREATE_STRATEGY
        model = None
        abstract = True

    _SEQUENCE = 1
    _SEQUENCE_LOCK = threading.Lock()

    @classmethod
    def _setup_next_sequence(cls):
        with cls._SEQUENCE_LOCK:
            cls._SEQUENCE += 1
        return cls._SEQUENCE


@django.mute_signals(post_save)
class ProfileFactory(Factory):
    class Meta:
        model = Profile

    zip = LazyFunction(fake.zipcode)
    sign_in_count = LazyFunction(fake.random_digit)
    mentor = LazyFunction(fake.pybool)
    state = LazyFunction(fake.state)
    address_1 = fake.street_address()
    address_2 = None
    city = LazyFunction(fake.city)
    branch_of_service = LazyFunction(random_branch)
    years_of_service = LazyAttribute(lambda x: fake.random_int(max=40))
    pay_grade = LazyFunction(random_pay_grade)
    military_occupational_specialty = LazyFunction(random_mos)

    user = SubFactory("tests.factories.UserFactory", profile=None)


@django.mute_signals(post_save)
class EmailAddressFactory(Factory):
    class Meta:
        model = EmailAddress

    primary = True
    verified = True
    user = SubFactory("tests.factories.UserFactory", active_email=None)


@django.mute_signals(post_save)
class UserFactory(Factory):
    class Meta:
        model = settings.AUTH_USER_MODEL
        strategy = CREATE_STRATEGY

    first_name = LazyFunction(fake.first_name)
    last_name = LazyFunction(fake.last_name)
    email = LazyFunction(fake.email)
    username = LazyAttribute(lambda o: o.email)
    password = PostGeneration(
        lambda obj, *args, **kwargs: obj.set_password(DEFAULT_PASSWORD)
    )
    profile = RelatedFactory(ProfileFactory, "user")
    active_email = RelatedFactory(EmailAddressFactory, "user", email=email)
