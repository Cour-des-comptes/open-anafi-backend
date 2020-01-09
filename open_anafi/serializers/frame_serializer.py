from rest_framework import serializers

from open_anafi.models import Frame, Indicator, Nomenclature
from open_anafi.serializers import IdentifierTypeSerializer, InstitutionTypeSerializer


class FrameSerializer(serializers.ModelSerializer):
    indicators = serializers.PrimaryKeyRelatedField(queryset = Indicator.objects.all(), allow_null = True, many=True, required = False)
    nomenclature = serializers.PrimaryKeyRelatedField(queryset = Nomenclature.objects.all(), required = False)
    identifiers_type = IdentifierTypeSerializer(many = True, required = False, read_only = True)
    institutions_type = InstitutionTypeSerializer(many = True, required = False, read_only = True)

    class Meta:
        model = Frame
        fields = ['id', 'name', 'description', 'indicators', 'nomenclature', 'identifiers_type', 'institutions_type', 'model_name']
