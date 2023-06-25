from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.db.models import UniqueConstraint

from users.models import User


class Ingredient(models.Model):
    """ Ингредиенты """

    name = models.CharField(
        'Наименование ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=100
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} в {self.measurement_unit}'


class Tag(models.Model):
    """ Тэги """

    name = models.CharField(
        'Название Тэга',
        unique=True,
        max_length=200
    )
    slug = models.SlugField(unique=True, db_index=True)
    color = models.CharField(
        'Цветовой HEX-код',
        max_length=7,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введите значение цвета в формате HEX! (например: #49B64E)'
            )
        ]
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    """ Рецепты """

    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        'Название рецепта',
        max_length=200
    )
    image = models.ImageField(
        'Изображение рецепта',
        upload_to='recipes/images/',
    )
    text = models.TextField(
        'Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )
    cooking_time = models.IntegerField(
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(
                1, 'Время приготовление должно быть не менее минуты'
            )
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации рецепта',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """ Модель создания рецепта """

    recipe = models.ForeignKey(
        Recipe,
        related_name='IngredientsInRecipe',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='IngredientsInRecipe',
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        'Колличество ингредиента',
        validators=[
            MinValueValidator(
                1, 'Колличество ингредиента в рецептне не должно быть менее 1.'
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте '
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'Игредиент {self.ingredient.name} в рецепте {self.recipe.name}'


class Favorite(models.Model):
    """ Избранные рецепты """

    user = models.ForeignKey(
        User,
        related_name='FavoriteRecipe',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='FavoriteRecipe',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'],
                             name='unique_favorite')
        ]

    def __str__(self):
        return f'Рецепт {self.recipe.name} в списке избанного у {self.user.username}'


class ShoppingCart(models.Model):
    """ Репепты в списке покупок """

    user = models.ForeignKey(
        User,
        related_name='RecipeInShoppingList',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='shopping_cart',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        constraints = [
            UniqueConstraint(fields=['user', 'recipe'],
                             name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'Рецепт {self.recipe.name} в списке покупок у {self.user.username}'
