from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from open_anafi.lib import IsAdminOrReadOnly
from open_anafi.models import Nomenclature
from open_anafi.serializers import NomenclatureSerializer


class NomenclatureViewsSet(viewsets.ModelViewSet):
    queryset = Nomenclature.objects.all()
    serializer_class = NomenclatureSerializer
    permission_classes = (IsAuthenticated, IsAdminOrReadOnly)

    def destroy(self, request, pk):
        frame_id = pk

        try:
            nomenclature = Nomenclature.objects.get(id = frame_id)
        except ObjectDoesNotExist:
            return Response(status = 404)

        frames = nomenclature.frames.all()
        frames.delete()
        nomenclature.delete()

        return Response(status = 200)
