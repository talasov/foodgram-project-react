from django.contrib import admin

from .models import User, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """ Класс пользователя """

    list_display = '__all__'
    search_fields = ('username',)
    list_filter = ('username', 'email')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """ Отображение подписок пользователя на автора """

    list_display = ('user', 'author')
