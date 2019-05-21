from copy import deepcopy

DEFAULT_USER = {
    "first_name": "FIRST",
    "last_name": "LAST",
    "profile": {
        "zip": "55555",
        "sign_in_count": 1,
        "mentor": False,
        "state": "CA",
        "address_1": "123 Fake Street",
        "address_2": "",
        "city": "Fake City",
        "branch_of_service": "army",
        "years_of_service": 1.0,
        "pay_grade": "E1",
        "military_occupational_specialty": "99Z",
    },
}

FLATTENED_USER = deepcopy(DEFAULT_USER)
profile = FLATTENED_USER.pop("profile")

for key, val in profile.items():
    FLATTENED_USER[key] = val
