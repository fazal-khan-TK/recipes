"""
Tests for models.
"""

from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class ModelTests(TestCase):
    """Test models."""
    
    #======================
    #     User Models
    #======================

    def test_create_user_with_email_success(self):
        """Test creating user with email is succesful."""
        email = 'test@example.com'
        password = 'password'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test new user email is automatically normalized."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creating a new user without an email fails."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test1234')

    def test_create_superuser(self):
        """Test that creating a superuser works correctly."""
        user = get_user_model().objects.create_superuser('test@example.com', 'sample123')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)


    #======================
    #     Recipe Models
    #======================

    def test_create_recipe_success(self):
        """Test creating a recipe is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Test Recipe',
            description='A test recipe',
        )
        self.assertEqual(str(recipe), recipe.title)


    #======================
    #     Ingredient Models
    #======================

    def test_create_ingredient(self):
        """Test creating an ingredient is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Test Ingredient',
        )
        self.assertEqual(str(ingredient), ingredient.name)