from open_anafi.models import TranslationTableEstablishmentType
from rest_framework import serializers

class TranslationTableEstablishmentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranslationTableEstablishmentType
        fields = ['id', 'type_budget', 'letter', 'type_establishment']