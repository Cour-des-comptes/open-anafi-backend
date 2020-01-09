from rest_framework import serializers
from open_anafi.models import Variable, IndicatorParameter 

class VariableSerializer(serializers.ModelSerializer):
    indicator_parameter = serializers.PrimaryKeyRelatedField(queryset = IndicatorParameter.objects.all(), allow_null = True, required = False)

    class Meta:
        model = Variable
        fields = ['id', 'name', 'numero_compte', 'type_solde', 'solde', 'indicator_parameter']
