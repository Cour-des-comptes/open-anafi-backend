from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions
from django.conf import settings
import jwt

class JWTAuthentication(authentication.BaseAuthentication):
	def authenticate(self, request):
		return_value = None
		if 'HTTP_AUTHORIZATION' in request.META:
			token = request.META.get('HTTP_AUTHORIZATION')[7:]
			try:
				decoded = jwt.decode(token.encode('utf-8'), settings.JWT_KEY, algorithm='HS256')
			except jwt.exceptions.InvalidSignatureError:
				raise exceptions.AuthenticationFailed('Invalid token')
			except jwt.exceptions.DecodeError:
				raise exceptions.AuthenticationFailed('Invalid token')

			user = User.objects.get(username=decoded.get('username'))
			user.is_staff = decoded.get('admin')
			return_value = (user, None)  #Auth successful
		return return_value
