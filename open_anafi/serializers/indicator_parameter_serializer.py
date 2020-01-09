from open_anafi.models import IndicatorParameter, Indicator
from rest_framework import serializers


class IndicatorParameterSerializer(serializers.ModelSerializer):
    indicator = serializers.PrimaryKeyRelatedField(queryset = Indicator.objects.all(), allow_null = True, required = False)

    class Meta:
        model = IndicatorParameter
        fields = ['id', 'indicator', 'year_min', 'year_max', 'readable_equation', 'original_equation', 'depth']