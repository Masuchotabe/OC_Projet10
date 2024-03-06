from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils.translation import gettext_lazy as _


class User(AbstractUser):

    birth_date = models.DateField(_('Birth date'))
    can_be_contacted = models.BooleanField(_("Can be contacted"))
    can_data_be_shared = models.BooleanField(_("Accept to share data"))

    REQUIRED_FIELDS = []
