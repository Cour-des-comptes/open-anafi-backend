from rest_framework.views import APIView
from rest_framework.response import Response
from open_anafi.models import Indicator, IndicatorLibelle
from open_anafi.serializers.indicator_serializer import LibelleSerializer
from django.core.exceptions import ObjectDoesNotExist
class IndicatorLibelleView(APIView):
    def post(self, request, pk):
        libelle = request.data.get('libelle')

        try:
            indicator = Indicator.objects.get(id=pk)
        except ObjectDoesNotExist:
            raise Exception('Error while retrieving the indicator.')

        indicator_libelle = IndicatorLibelle.objects.create(libelle=libelle, indicator=indicator)
        indicator_libelle.save()
        return Response(LibelleSerializer(indicator_libelle).data)