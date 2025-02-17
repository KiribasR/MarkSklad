from django.db import models

class Search(models.Model):
    searchField = models.CharField('Поиск', max_length=100)

    def __str__(self):
        return self.searchField

    class Meta:
        verbose_name = 'Поисковый запрос'
        verbose_name_plural = 'Поисковые запросы'