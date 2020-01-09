from rest_framework import serializers
from open_anafi.models import Indicator, Frame, IndicatorLibelle
from open_anafi.serializers import IndicatorParameterSerializer


class LibelleSerializer(serializers.ModelSerializer):
    indicator = serializers.PrimaryKeyRelatedField(queryset = Indicator.objects.all(), many=False, required=False)

    class Meta:
        model = IndicatorLibelle
        fields = ['libelle', 'indicator']

class IndicatorSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length = 100)
    frames = serializers.PrimaryKeyRelatedField(queryset = Frame.objects.all(), many = True, required = False)
    parameters = IndicatorParameterSerializer(many=True, required=False)
    libelles = LibelleSerializer(many=True, required=False)

    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary eager loading of data. """
        queryset = queryset.prefetch_related('parameters')
        queryset = queryset.prefetch_related('frames')
        queryset = queryset.prefetch_related('libelles')
        return queryset

    class Meta:
        model = Indicator
        fields = ['id', 'name', 'description', 'frames', 'max_depth', 'parameters', 'public', 'last_modified_by', 'libelles']
