from rest_framework import viewsets

from core.models import Recipe
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer
)


class RecipeViewSet(viewsets.ModelViewSet):
    """View for managing recipe APIs."""

    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        """Return serializer class for the request."""
        if self.action == 'list':
            return RecipeSerializer
        return self.serializer_class
