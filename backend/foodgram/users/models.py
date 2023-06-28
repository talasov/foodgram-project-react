from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    """ Модель пользователя """

    USER = 'user'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'user'),
        (ADMIN, 'admin'),
    ]
    username = models.CharField(
        'username',
        max_length=150,
        unique=True
    )
    email = models.EmailField(
        'email',
        max_length=254,
        blank=False,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False
    )
    password = models.CharField(
        'Пароль',
        max_length=150,
    )

    role = models.CharField(
        choices=ROLE_CHOICES,
        max_length=10,
        verbose_name='Роль пользователя',
        default=USER
    )
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name='user_groups',
        verbose_name='groups',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='user_permissions',
        verbose_name='user permissions',
        related_query_name='user',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'last_name', 'first_name', ]

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """ Подписки на авторов """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_subscription')
        ]

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
