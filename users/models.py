from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    company = models.CharField(max_length=120, blank=True)

    def __str__(self) -> str:
        return self.username
