"""
Tests for the Recipe API.
"""


from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from core.models import Ingredient

from core.models import Recipe

from recipe.serializers import (RecipeSerializer, RecipeDetailSerializer)


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(**params):
    """Create and return a recipe."""
    defaults = {
        'name': 'Test Recipe',
        'description': 'Test description.',
    }
    defaults.update(params)
    recipe = Recipe.objects.create(**defaults)
    return recipe


class RecipeApiTests(TestCase):
    """Test the recipe API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_recipe_success(self):
        """Test creating a recipe via POST request."""
        payload = {
            'name': 'Sample recipe',
            'description': 'this is a description',
            'ingredients': [{'name': 'Salt'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_success(self):
        """Test retrieving a list of recipes."""
        recipe_a = create_recipe(name='Salt')
        recipe_b = create_recipe(name='Pepper')
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(recipes.count(), 2)
        self.assertIn(recipe_a, recipes.all())
        self.assertIn(recipe_b, recipes.all())

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe()
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_update_recipe(self):
        """Test updating recipe ingredients."""
        # First create the recipe using a POST request
        payload = {
            'name': 'Salt & Pepper Soup',
            'ingredients': [{'name': 'Salt'}, {'name': 'Pepper'}],
            'description': 'a made up recipe'
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.first()
        salt = Ingredient.objects.filter(name='Salt').first()
        pepper = Ingredient.objects.filter(name='Pepper').first()
        self.assertIn(salt, recipe.ingredients.all())
        self.assertIn(pepper, recipe.ingredients.all())
        # now update the recipe
        patch_payload = {
            'ingredients': [{'name': 'Lime'}]
        }
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, patch_payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        lime = Ingredient.objects.filter(name='Lime').first()
        self.assertIn(lime, recipe.ingredients.all())

    def test_delete_recipe_success(self):
        """Test deleting a recipe via DELETE request."""
        recipe = create_recipe()
        recipes = Recipe.objects.all()
        self.assertEqual(recipes.count(), 1)
        url = detail_url(recipe_id=recipe.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(recipes.count(), 0)
