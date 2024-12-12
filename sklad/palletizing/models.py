from django.db import models

class PalletCode(models.Model):
    palletField = models.CharField('Код паллета', max_length=30)

    def __str__(self):
        return self.palletField

    class Meta:
        verbose_name = 'Код паллета'
        verbose_name_plural = 'Коды паллетов'


class AggregateCode(models.Model):
    aggregateField = models.CharField('Код агрегата', max_length=50)

    def __str__(self):
        return self.aggregateField

    class Meta:
        verbose_name = 'Код агрегата'
        verbose_name_plural = 'Коды агрегатов'
