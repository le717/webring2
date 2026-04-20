# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
from .base import BASE_DIR


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
SITE_TITLE = "Webring"
