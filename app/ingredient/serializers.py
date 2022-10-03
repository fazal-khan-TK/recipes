
from rest_framework import serializers
from core.models import Ingredient

class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""
    class Meta:
        model = Ingredient
        fields = ['name']
        read_only_fields = ['id']