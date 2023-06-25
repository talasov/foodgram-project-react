from csv import DictReader

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Загрузка данных из ingredient.csv"

    def handle(self, *args, **options):
        print("Загрузка ингредиентов.")

        count = 0
        for row in DictReader(
            open('./data/ingredients.csv', encoding='utf-8')
        ):
            ingredient = Ingredient(
                name=row['name'],
                measurement_unit=row['m_unit']
            )
            ingredient.save()
            count += 1

        print(f'Успешно загружено {count} ингредиентов')