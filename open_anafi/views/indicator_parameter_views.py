from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from open_anafi.lib import print_tree_graph
from open_anafi.models import IndicatorParameter
from open_anafi.serializers import IndicatorParameterSerializer


class IndicatorParameterViewsSet(viewsets.ModelViewSet):
    queryset = IndicatorParameter.objects.all()
    serializer_class = IndicatorParameterSerializer
    lookup_value_regex = '[0-9]+'
    permission_classes = (IsAuthenticated,)

    def generate_tree(self, pk):
        try:
            indicator_parameter = IndicatorParameter.objects.get(id = pk)
            try:
                eq = eval(indicator_parameter.readable_equation)
            except NameError:
                eq = indicator_parameter.readable_equation
            print_tree_graph(eq, f"/opt/backend/graph_renders/{indicator_parameter.indicator.name}_{indicator_parameter.id}")
            return Response({'Ok'}, status = 200)
        except Exception as e:
            return Response({'error': str(e)}, status = 500)
            
        