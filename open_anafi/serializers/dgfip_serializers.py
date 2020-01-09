from rest_framework import serializers
from open_anafi.models import Department, InstitutionType, IdentifierType

class IdentifierTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model = IdentifierType
		fields = ['name']

class InstitutionTypeSerializer(serializers.ModelSerializer):
		class Meta:
				model = InstitutionType
				fields = ['id', 'name', 'number', 'legal_status']

class DepartmentSerializer(serializers.ModelSerializer):
		class Meta:
				model = Department
				fields = ['id', 'name', 'number']