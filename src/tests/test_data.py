from enum import Enum

from faker import Factory as FakerFactory

fake = FakerFactory.create()

DEFAULT_PASSWORD = "P4ssw0rd1"


def random_branch():
    return fake.random_element(
        elements=("army", "marine", "navy", "airforce", "coastguard")
    )


def random_text():
    return fake.random_text(max_nb_chars=200)


def random_pay_grade():
    return f"{fake.random_element(('E', 'O'))}{fake.random_digit()}"


def random_mos():
    return (
        f"{fake.random_number(digits=2, fix_len=True)}{fake.random_uppercase_letter()}"
    )


class UpdateProfileForm(Enum):
    """
    Represents the stateful PATCH's received from the
    frontend
    """

    empty_update = {}

    professional_details = {
        "employment_status": "fulltime",
        "company_name": "company",
        "company_role": "role",
        "military_status": None,
        "branch_of_service": None,
        "years_of_service": None,
        "pay_grade": None,
        "interests": None,
    }
    military_status = {
        "employment_status": "fulltime",
        "company_name": "company",
        "company_role": "role",
        "military_status": "veteran",
        "branch_of_service": None,
        "years_of_service": None,
        "pay_grade": None,
        "interests": None,
    }

    military_details = {
        "employment_status": "fulltime",
        "company_name": "company",
        "company_role": "role",
        "military_status": "veteran",
        "branch_of_service": "army",
        "years_of_service": 1,
        "pay_grade": "E1",
    }

    interests_empty = {
        "employment_status": "fulltime",
        "company_name": "company",
        "company_role": "role",
        "military_status": "veteran",
        "branch_of_service": "army",
        "years_of_service": 1,
        "pay_grade": "E1",
        "interests": "",
    }

    interests_single = {
        "employment_status": "fulltime",
        "company_name": "company",
        "company_role": "role",
        "military_status": "veteran",
        "branch_of_service": "army",
        "years_of_service": 1,
        "pay_grade": "E1",
        "interests": "React",
    }

    interests_multiple = {
        "employment_status": "fulltime",
        "company_name": "company",
        "company_role": "role",
        "military_status": "veteran",
        "branch_of_service": "army",
        "years_of_service": 1,
        "pay_grade": "E1",
        "interests": "React, Java",
    }
