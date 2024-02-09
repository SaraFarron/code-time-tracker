from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import password_changed
from django.db import models
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name=_("user")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("created_at")
    )
    wakatime_created_at = models.DateTimeField(
        verbose_name=_("wakatime_created_at")
    )
    wakatime_token = models.CharField(
        max_length=255, verbose_name=_("wakatime_token")
    )

    _wakatime_token = None

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self._wakatime_token is not None:
            password_changed(self._wakatime_token, self)
            self._wakatime_token = None

    def set_wakatime_token(self, raw_wakatime_token):
        self.wakatime_token = make_password(raw_wakatime_token)
        self._wakatime_token = raw_wakatime_token


class Day(models.Model):
    date = models.DateField(verbose_name=_("date"))
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, verbose_name=_("profile")
    )

    def __str__(self) -> str:
        return str(self.date)

    class Meta:
        unique_together = ("date", "profile")
        verbose_name = _("day")
        verbose_name_plural = _("days")


class WakatimeData(models.Model):
    CATEGORIES = (
        ("CATEGORIES", 'categories'),
        ("EDITORS", 'editors'),
        ("LANGUAGES", 'languages'),
        ("MACHINES", 'machines'),
        ("SYSTEMS", 'operating_systems'),
        ("PROJECTS", 'projects'),
    )

    category = models.CharField(
        choices=CATEGORIES, max_length=10, verbose_name=_("category")
    )
    decimal = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("decimal")
    )
    digital = models.DurationField(verbose_name=_("digital"))
    name = models.CharField(max_length=255, verbose_name=_("name"))
    total_seconds = models.FloatField(verbose_name=_("total_seconds"))
    percent = models.DecimalField(
        max_digits=3, decimal_places=2, verbose_name=_("percent")
    )
    day = models.ForeignKey(
        Day, on_delete=models.CASCADE, verbose_name=_("day")
    )

    class Meta:
        unique_together = ("category", "name")
        verbose_name = _("wakatime data")
        verbose_name_plural = _("wakatime data")

    def __str__(self) -> str:
        return f"{self.category} - {self.name}"

    @property
    def hours(self):
        return self.total_seconds // 3600

    @property
    def minutes(self):
        return self.total_seconds // 60

    @property
    def text(self):
        return f"{self.hours}hrs {self.minutes}mins"
