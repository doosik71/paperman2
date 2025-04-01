from django.db import models


class Config(models.Model):
    key = models.CharField(max_length=256, blank=False, null=False, unique=True)
    value = models.TextField(blank=True)

    def __str__(self):
            return self.key


def get_config_value(key) -> str:
    config = Config.objects.all().filter(key=key)

    return config[0].value if len(config) else ""


def set_config_value(key, value) -> None:
    config = Config.objects.all().filter(key=key)

    if len(config):
        config[0].value = value
        config[0].save()
    else:
        Config.objects.create(key=key, value=value)
