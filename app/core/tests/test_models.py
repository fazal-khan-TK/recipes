"""
Tests for models.
"""

from django.test import TestCase
from core import models


class ModelTests(TestCase):
    """Test models."""

    def test_create_recipe_success(self):
        """Test creating a recipe is successful."""
        recipe = models.Recipe.objects.create(
            name='Test Recipe',
            description='A test recipe',
        )
        self.assertEqual(str(recipe), recipe.name)

    def test_create_ingredient(self):
        """Test creating an ingredient is successful."""
        recipe = models.Recipe.objects.create(
            name='Test Recipe',
            description='A test recipe',
        )
        ingredient = models.Ingredient.objects.create(
            recipe=recipe,
            name='Test Ingredient',
        )
        self.assertEqual(str(ingredient), ingredient.name)
