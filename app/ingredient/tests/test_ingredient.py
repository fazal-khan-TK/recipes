from django.test import TestCase
from core.models import Ingredient, Recipe

from ingredient.serializers import IngredientSerializer


class IngredientApiTests(TestCase):
    """Test the unauthenticated parts of the ingredient API."""

    def test_serialize_ingredient(self):
        """Test succesfully getting an ingredient."""
        recipe = Recipe.objects.create(
            name='Soup',
            description='description'
        )
        Ingredient.objects.create(name='Carrot', recipe=recipe)
        ingredients = Ingredient.objects.all().first()
        serializer = IngredientSerializer(ingredients)
        self.assertEqual(serializer.data, {'name': 'Carrot'})

    