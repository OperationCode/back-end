from pathlib import Path

from decouple import AutoConfig

# Loading `.env` files
# See docs: https://gitlab.com/mkleehammer/autoconfig
config = AutoConfig()

# Build paths inside the project like this: BASE_DIR / 'some'
# `pathlib` is better than writing: dirname(dirname(__file__))
BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENVIRONMENT = config("ENVIRONMENT", default="local")
