from django.db import models
from django.contrib.auth import get_user_model

from yatube.settings import POST_SYMBOLS, COMMENT_SYMBOLS

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(
        max_length=200,
        blank=True
    )

    class Meta:
        ordering = ['title', ]

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Добавьте текст для новой записи'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу для новой записи',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date', ]

    def __str__(self):
        return self.text[:POST_SYMBOLS]


class Comment(models.Model):
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        related_name='comment',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='comment',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        verbose_name='Текст',
        help_text='Прокомментировать'
    )

    class Meta:
        ordering = ['-created', ]

    def __str__(self):
        return self.text[:COMMENT_SYMBOLS]
