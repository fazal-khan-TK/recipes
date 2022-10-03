from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

def detail_url(ingredient_id):
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='user@example.com', password='testpass123'):
    return get_user_model().objects.create_user(
        email=email,
        password=password,
    )

class PublicIngredientApiTests(TestCase):
    """Test the unauthenticated parts of the ingredient API."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth required for returning ingredients."""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test authenticated API routes."""

    def setUp(self):
        # we force login a user to avoid having to authenticate on every test.
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredient_success(self):
        """Test succesfully retrieving an ingredient."""
        Ingredient.objects.create(user=self.user, name='Carrot')
        Ingredient.objects.create(user=self.user, name='Peas')
        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user only."""
        other_user = create_user(
            email='other@example.com',
            password='testpass123'
        )
        # create recipes for other user
        Ingredient.objects.create(user=other_user, name='Pepper')
        # create recipes for authenticated user
        Ingredient.objects.create(user=self.user, name='Salt')
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredients = Ingredient.objects.filter(user=self.user)
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_update_ingredient(self):
        """Test updating ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')

        payload = {'name': 'Coriander'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])


    def test_delete_ingredient(self):
        """Test deleting ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')

        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredient = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredient.exists())