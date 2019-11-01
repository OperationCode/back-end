"""
Configs for the temporary frontend app
"""
from settings.components import config

RECAPTCHA_PUBLIC_KEY = config("RECAPTCHA_PUBLIC_KEY", default="")
RECAPTCHA_PRIVATE_KEY = config("RECAPTCHA_PRIVATE_KEY", default="")
GITHUB_JWT = config("GITHUB_JWT", default="")
GITHUB_REPO = config("GITHUB_REPO", default="")
