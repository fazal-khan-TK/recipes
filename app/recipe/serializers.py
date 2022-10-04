from rest_framework import serializers
from core.models import Recipe, Ingredient
from ingredient.serializers import IngredientSerializer


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'ingredients']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for detailed recipe view"""
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients"""
        for ingredient in ingredients:
            ingredient_obj, _ = Ingredient.objects.get_or_create(
                **ingredient,
                recipe=recipe
            )
            recipe.ingredients.add(ingredient_obj)

    def create(self, validated_data):
        """Create a recipe."""
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.all().delete()
            self._get_or_create_ingredients(ingredients, instance)
        super().update(instance, validated_data)
        return instance
