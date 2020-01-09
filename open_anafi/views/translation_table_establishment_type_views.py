from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from open_anafi.models import TranslationTableEstablishmentType
from open_anafi.serializers import TranslationTableEstablishmentTypeSerializer


class TranslationTableEstablismentTypeViewsSet(viewsets.ModelViewSet):
    queryset = TranslationTableEstablishmentType.objects.all()
    serializer_class = TranslationTableEstablishmentTypeSerializer
    permission_classes = (IsAuthenticated,)
