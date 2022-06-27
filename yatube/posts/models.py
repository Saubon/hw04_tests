from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(unique=True, verbose_name='Имя страницы')
    description = models.TextField(blank=False, verbose_name='Описание')

    class Meta:
        verbose_name = 'группу'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        blank=False,
        verbose_name='Текст',
        help_text='Введите текст'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Введите название вашей группы'
    )

    class Meta:
        verbose_name = 'запись'
        verbose_name_plural = 'Записи'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]
