from settings.components import config

# OperationCode Slackbot
# https://github.com/OperationCode/operationcode-pybot
PYBOT_AUTH_TOKEN = config("PYBOT_AUTH_TOKEN", default="")
PYBOT_URL = config("PYBOT_URL", default="http://localhost:5000")

# Mailchimp3
# https://pypi.org/project/mailchimp3/
MAILCHIMP_API_KEY = config("MAILCHIMP_API_KEY", default="")
MAILCHIMP_USERNAME = config("MAILCHIMP_USERNAME", default="")
MAILCHIMP_LIST_ID = config("MAILCHIMP_LIST_ID", default="")

# Mandrill anymail configs
MANDRILL_API_KEY = config("MANDRILL_API_KEY", default="")
if MANDRILL_API_KEY:  # pragma: no cover
    ANYMAIL = {"MANDRILL_API_KEY": MANDRILL_API_KEY}
