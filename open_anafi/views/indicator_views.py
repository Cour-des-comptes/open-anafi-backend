from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from open_anafi.lib import parse_indicator
from open_anafi.lib.indicator_tools import IndicatorTools
from open_anafi.models import Indicator
from open_anafi.serializers import IndicatorSerializer


class IndicatorViews(viewsets.ModelViewSet):
    serializer_class = IndicatorSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):

        frame_id = self.request.query_params.get('frame', None)

        if frame_id is not None:
            queryset = Indicator.objects.all()
            queryset = queryset.filter(frames__id = frame_id)

        else:
            queryset = Indicator.objects.all()


        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset

    def create(self, request):
        name = request.data.get('name', None)
        description = request.data.get('description', None)
        equation = request.data.get('equation', None)
        libelle = request.data.get('libelle', None)
        if Indicator.objects.filter(name = name).count() > 0:
            raise Exception("Ce nom d'indicateur est déjà existant")
        parse_indicator(name, equation, description, public=False, user=request.user.username, libelle=libelle)

        created_indicator = Indicator.objects.get(name = name)

        return Response(data=IndicatorSerializer(created_indicator).data, status=201)

    def update(self, request, pk):
        description = request.data.get('description', None)
        equation = request.data.get('equation', None)
        libelle = request.data.get('libelle', None)

        indicator_name = IndicatorTools.update_indicator(equation, description, pk, libelle=libelle)
        updated_indicator = Indicator.objects.get(name=indicator_name)
        return Response(data=IndicatorSerializer(updated_indicator).data, status=200)

    def destroy(self, request, pk):

        return Response(status=200)

    @staticmethod
    def check_equation(request):
        """
        A view that receives an equation and raises an exception if the equation is wrong.

        """
        equation = request.data.get('original_equation')
        IndicatorTools.check_equation(equation)
        return Response(status=200)
