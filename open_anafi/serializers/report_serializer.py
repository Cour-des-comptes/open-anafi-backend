from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from open_anafi.models import Frame, Report, Department, InstitutionType


class MinLowerThanMax(object):

	message = "{max} field lower than {min} field"
	def __init__(self, min_field, max_field):
		self.min_field = min_field
		self.max_field = max_field

	def	__call__(self, attrs):
		if attrs[self.min_field] > attrs[self.max_field]:
			raise ValidationError(self.message.format(max = self.max_field, min = self.min_field))


class ReportSerializer(serializers.Serializer):
		frame = serializers.PrimaryKeyRelatedField(queryset = Frame.objects.all(), many = False, required = False)
		frame_name = serializers.CharField(max_length = 100, required = False)
		financial_year_min = serializers.IntegerField(required = True)
		financial_year_max = serializers.IntegerField(required = True)
		# identifiers = serializers.CharField(max_length = 100, required = True, many=True)
		identifiers = serializers.ListField(child=serializers.CharField(max_length = 100, required = True))
		identifiers_type = serializers.CharField(max_length = 100, required = True)

		class Meta:
				validators = [MinLowerThanMax('financial_year_min', 'financial_year_max')]

		def create(self, validated_data):
			pass

		def update(self, instance, validated_data):
			pass


class AggregatedReportSerializer(serializers.Serializer):
		frame = serializers.PrimaryKeyRelatedField(queryset=Frame.objects.all(), many=False, required=True)
		financial_year_min = serializers.IntegerField(required=True)
		financial_year_max = serializers.IntegerField(required=True)
		departments = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), many=True, required=True)
		institutions = serializers.PrimaryKeyRelatedField(queryset=InstitutionType.objects.all(), many=True, required=True)
		pop_max = serializers.IntegerField(required=False)
		pop_min = serializers.IntegerField(required=False)

		class Meta:
			validators = [MinLowerThanMax('financial_year_min', 'financial_year_max')]

		def create(self, validated_data):
			pass

		def update(self, instance, validated_data):
			pass



class ReportModelSerializer(serializers.ModelSerializer):
		frame = serializers.PrimaryKeyRelatedField(queryset=Frame.objects.all(), many=False, required=False)

		class Meta:
				model = Report
				fields = ['id', 'date', 'state', 'name', 'frame','frame_name', 'identifier', 'identifier_type', 'year_min', 'year_max']