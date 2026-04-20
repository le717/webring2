# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
from .base import BASE_DIR


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "webring.db",
    }
}
SITE_TITLE = "Webring"
