from django.db import models

class PalletCode(models.Model):
    palletField = models.CharField('Код паллета', max_length=100)

    def __str__(self):
        return self.palletField

    class Meta:
        verbose_name = 'Код паллета'
        verbose_name_plural = 'Коды паллетов'
