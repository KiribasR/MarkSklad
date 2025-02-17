from django.db import models
from django import forms


class PalletTask(models.Model):
    taskField = models.CharField('Задание', max_length=30)

    def __str__(self):
        return self.taskField

    class Meta:
        verbose_name = 'Номер задания'
        verbose_name_plural = 'Номера заданий'


class PalletCode(models.Model):
    palletField = models.CharField('Код паллета', max_length=40,blank=True)
    taskField = models.CharField('Код паллета', max_length=50, blank=True)
    curPallet = models.CharField('Код паллета', max_length=50, blank=True)

    def __str__(self):
        return self.palletField

    class Meta:
        verbose_name = 'Код паллета'
        verbose_name_plural = 'Коды паллетов'


class AggregateCode(models.Model):
    aggregateField = models.CharField('Код агрегата', max_length=50,blank=True)
    pallet = models.CharField('Код паллета', max_length=50, blank=True)
    task = models.CharField('Код паллета', max_length=50, blank=True)

    def __str__(self):
        return self.aggregateField

    class Meta:
        verbose_name = 'Код агрегата'
        verbose_name_plural = 'Коды агрегатов'
