from django.contrib import admin

from .models import (Recipe, Tag, IngredientInRecipe,
                     ShoppingCart, Favorite, Ingredient)


class RecipeIngredientInline(admin.TabularInline):
    model = IngredientInRecipe
    min_num = 1
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """ Админка Рецепта """

    inlines = (RecipeIngredientInline, )
    list_display = (
        'name', 'author', 'pub_date',
    )
    list_filter = ('name', 'author',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """ Админка Тэга """

    list_display = ('pk', 'name', 'slug', 'color',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """ Админка Ингредиента """

    list_display = ('pk', 'name', 'measurement_unit')


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """ Отображение ингредиентов и их кол-во в рецепте """

    list_display = ('recipe', 'ingredient', 'amount')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """ Избранные рецепты пользователей """

    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """ Отображения списка покупок """

    list_display = ('user', 'recipe')
