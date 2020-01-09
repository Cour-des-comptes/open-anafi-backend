from open_anafi.models import Nomenclature
from rest_framework import serializers

class NomenclatureSerializer(serializers.ModelSerializer):

    class Meta:
        model = Nomenclature
        fields = ['id', 'name', 'description']