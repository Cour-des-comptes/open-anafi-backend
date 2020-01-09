from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class UsersViews(APIView):
	@staticmethod
	def post(request):
		username = request.data.get('username')
		is_admin = True
		try:
			user = User.objects.get(username=username)
		except ObjectDoesNotExist:
			User.objects.create(username=username, is_staff=is_admin)

		encoded_jwt = jwt.encode(
			{
				'username': username,
				'admin': is_admin,
				'exp': datetime.utcnow() + timedelta(hours=12)
			},
			settings.JWT_KEY,
			algorithm='HS256')
		return Response({'token': encoded_jwt}, status = 200)

	@permission_classes((IsAuthenticated,))
	def get(self, request):
		name = request.user.username
		json_response = {"name": name, "isAdmin": request.user.is_staff}
		return Response(json_response)

