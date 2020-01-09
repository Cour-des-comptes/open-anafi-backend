from rest_framework import viewsets
from open_anafi.models import Frame, InstitutionType, IdentifierType, Nomenclature
from open_anafi.serializers import FrameSerializer
from open_anafi.lib import IsAdminOrReadOnly
from open_anafi.lib import FrameTools
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage, FileSystemStorage
from django.conf import settings
from django.core.files.base import ContentFile
import os
from open_anafi.lib import parse_excel_file
from django.core.exceptions import ObjectDoesNotExist

class FrameViewsSet(viewsets.ModelViewSet):
	queryset = Frame.objects.all()
	serializer_class = FrameSerializer
	permission_classes = (IsAuthenticated, IsAdminOrReadOnly)
	parser_classes = (MultiPartParser,)

	def create(self, request, **kwargs):
		settings_file = request.FILES.get('settings_file', None)
		template_file = request.FILES.get('template_file', None)

		institution_types = request.data.get('institution_types', '')
		institution_types = list(filter(None, institution_types.split(',')))
		
		identifier_types = request.data.get('identifier_types', '')
		identifier_types = list(filter(None, identifier_types.split(',')))
		
		frame_data = request.data.get('frame_name', '')
		frame_description = request.data.get('frame_description', '')
		nomenclature = request.data.get('nomenclature')

		if template_file is not None:
			template_storage = FileSystemStorage(location=settings.TEMPLATES_ROOT)
			template_storage.delete(settings.BASE_DIR + '/open_anafi/templates/' + template_file.name)
			template_storage.save(settings.BASE_DIR + '/open_anafi/templates/' + template_file.name, ContentFile(template_file.read()))
			FrameTools.get_or_create_frame(frame_data, template_file.name, frame_description, nomenclature, institution_types, identifier_types)
		else:
			FrameTools.get_or_create_frame(frame_data, None, frame_description, nomenclature, institution_types, identifier_types)

		if settings_file is not None:
			settings_file_path = default_storage.save('tmp/' + settings_file.name, ContentFile(settings_file.read()))
			tmp_file = os.path.join(settings.MEDIA_ROOT, settings_file_path)

			if template_file is not None:
				parse_excel_file(tmp_file, institution_types, identifier_types, frame_data.strip(), frame_description, nomenclature, template_file.name, user=request.user.username)
			else:
				parse_excel_file(tmp_file, institution_types, identifier_types, frame_data.strip(), frame_description, nomenclature, user=request.user.username)

		return Response()


	def destroy(self, request, pk):
		frame_id = pk

		try:
			frame = Frame.objects.get(id = frame_id)
		except ObjectDoesNotExist:
			return Response(status = 404)

		frame.delete()

		return Response(status = 200)

	def update(self, request, pk):
		try:
			frame = Frame.objects.get(id = pk)
		except ObjectDoesNotExist:
			raise Exception("Unknown frame id.")

		#Retrieve data
		template_file = request.FILES.get('template_file', None)

		institution_types = request.data.get('institution_types', '')
		institution_types = list(filter(None, institution_types.split(',')))
		
		identifier_types = request.data.get('identifier_types', '')
		identifier_types = list(filter(None, identifier_types.split(',')))

		frame_data = request.data.get('frame_name', '')
		frame_description = request.data.get('frame_description', '')
		nomenclature = request.data.get('nomenclature', '')

		#Update
		frame.name = frame_data
		frame.description = frame_description

		frame.institutions_type.clear()
		frame.identifiers_type.clear()

		for institution_type in institution_types:
			frame.institutions_type.add(InstitutionType.objects.get(number = int(institution_type)))
		for identifier_type in identifier_types:
			frame.identifiers_type.add(IdentifierType.objects.get(name = identifier_type))

		try:
			frame.nomenclature = Nomenclature.objects.get(id = nomenclature)
		except Exception as e:
			raise Exception(str(e))
		
		if template_file is not None:
			template_storage = FileSystemStorage(location=settings.TEMPLATES_ROOT)
			template_storage.delete(settings.BASE_DIR + '/open_anafi/templates/' + template_file.name)
			template_storage.save(settings.BASE_DIR + '/open_anafi/templates/' + template_file.name, ContentFile(template_file.read()))
			frame.model_name = template_file.name

		frame.save()

		return Response(data={'frame': FrameSerializer(frame).data}, status=200)


