from django.db import models
from core.models import User
# Create your models here.


# token for sign in users in aggregator
class TokenAggregatorModel(models.Model):
    class Meta:
        verbose_name = "Доступ к агрегатору"
        verbose_name_plural = "Доступы к агрегатору"

    token = models.CharField(unique=True, max_length=255, null=False, blank=False, verbose_name="Токен пользователя для агрегатора")
    user = models.OneToOneField(to=User, on_delete=models.CASCADE, null=False, blank=False, verbose_name="Пользователь", related_name="aggregator_token")

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name
