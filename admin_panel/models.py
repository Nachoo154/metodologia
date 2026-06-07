from django.core.validators import MinValueValidator
from django.db import models


class Configuracion(models.Model):
    stock_minimo = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        verbose_name = "Configuración"
        verbose_name_plural = "Configuración"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
