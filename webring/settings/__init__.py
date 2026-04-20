"""
This is a django-split-settings main file.

For more information read this:
https://github.com/sobolevn/django-split-settings
https://sobolevn.me/2017/04/managing-djangos-settings
"""

from split_settings.tools import include, optional


_base_settings = (
    "base.py",
    "audit.py",
    "i18n.py",
    optional("local.py"),
)
include(*_base_settings)
