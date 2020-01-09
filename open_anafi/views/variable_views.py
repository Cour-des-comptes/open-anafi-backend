"""
    @Name: Arthur Valingot
    @Date 16/10/2018
    @purpose: Create a view for the variable
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from open_anafi.models import Variable
from open_anafi.serializers import VariableSerializer


class VariableViewsSet(viewsets.ModelViewSet):

    queryset = Variable.objects.all()
    serializer_class = VariableSerializer
    permission_classes = (IsAuthenticated,)
