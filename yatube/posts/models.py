from django.contrib.auth import get_user_model
from django.db import models

from .constants import TESTS_NUMBER

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок')

    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='URL адрес группы')

    description = models.TextField(
        max_length=200,
        verbose_name='Описание',
        blank=True,
        null=True)

    def __str__(self):
        return f'{self.title}'


class Post(models.Model):
    text = models.TextField(
        max_length=400,
        verbose_name='Текст поста',
        help_text='Введите текст поста')

    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации')

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор')

    group = models.ForeignKey(
        Group, blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа поста')

    image = models.ImageField(
        verbose_name='Картинка',
        help_text='Загрузите картинку',
        upload_to='posts/',
        blank=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = 'Посты'
        verbose_name = 'Пост'

    def __str__(self):
        return self.text[:TESTS_NUMBER]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
        help_text='Пост, к которому относиться комментарий')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор')

    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария')

    created = models.DateTimeField(
        verbose_name='Дата комментария',
        auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_author_user_following'
            )
        ]
