from jose import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import requests

class SupabaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None  # endpoint público

        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            raise AuthenticationFailed("Token mal formado")

        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated"
            )
        except Exception:
            raise AuthenticationFailed("Token inválido")

        # Usuario virtual (no Django User)
        return (payload, None)