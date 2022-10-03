"""
Tests for the Recipe API.
"""


from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Recipe, Ingredient

from recipe.serializers import (RecipeSerializer, RecipeDetailSerializer)


RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])



def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)

def create_recipe(user, **params):
    """Create and return a recipe."""
    defaults = {
        'title': 'Test Recipe',
        'description': 'Test description.',
    }
    defaults.update(params)
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeApiTests(TestCase):
    """Test the unauthenticated parts of the recipe API."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test is required to call API."""
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test the authenticated parts of the recipe API."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user only."""
        other_user = create_user(
            email='other@example.com',
            password='testpass123'
        )
        # create recipes for other user
        create_recipe(user=other_user)
        create_recipe(user=other_user)
        # create recipes for authenticated user
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)



    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)


    def test_create_recipe(self):
        """Test creating a recipe via POST request."""
        payload = {
            'title': 'Sample recipe',
            'description': 'this is a description',
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(self.user, recipe.user)
        


    def test_create_recipe_with_new_ingredient(self):
        """Test creating a recipe with new ingredients."""
        payload = {
            'title': 'tomatoes soup',
            'description': ' a soup made of tomatoes',
            'ingredients': [{'name': 'tomatoes'}, {'name': 'salt'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)


    def test_create_recipe_with_existing_ingredient(self):
        """Test creating a recipe with existing ingredients."""
        ingredient = Ingredient.objects.create(user=self.user, name='tomatoes')
        payload = {
            'title': 'tomatoes soup',
            'description': ' a soup made of tomatoes',
            'ingredients': [{'name': 'tomatoes'}, {'name': 'salt'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists = recipe.ingredients.filter(
                name=ingredient['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        recipe = create_recipe(user=self.user)
        payload = {
            'ingredients': [{'name': 'Limes'}],
        }
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ingredient = Ingredient.objects.get(user=self.user, name='Limes')
        self.assertIn(new_ingredient, recipe.ingredients.all())

    def test_update_recipe_assign_ingredient(self):
        # create the pepper ingredient for the current user
        ingredient1 = Ingredient.objects.create(user=self.user, name='Pepper')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ingredient1)

        # create another salt ingredient for the user
        ingredient2 = Ingredient.objects.create(user=self.user, name='Salt')
        payload = {
            'ingredients': [{'name': 'Salt'}]
        }
        # check that the recipe has correctly updated
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())