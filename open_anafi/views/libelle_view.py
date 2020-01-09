from rest_framework.response import Response
from rest_framework.views import APIView

from open_anafi.models import IndicatorLibelle
from open_anafi.serializers.indicator_serializer import LibelleSerializer


class LibelleView(APIView):
    def update(self, request, pk):
        libelle = request.data.get('libelle')
        indicator_libelle = IndicatorLibelle.objects.get(id=pk)
        indicator_libelle.libelle = libelle
        indicator_libelle.save()
        return Response(LibelleSerializer(indicator_libelle).data)

    def delete(self, request, pk):
        indicator_libelle = IndicatorLibelle.objects.get(id=pk)
        indicator_libelle.delete()
        return Response({'deleted': True})

    def get(self, request):
        response = [LibelleSerializer(libelle).data for libelle in IndicatorLibelle.objects.all()]
        return Response(response)