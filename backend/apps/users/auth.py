from jose import jwt
from jose import jwk
from jose.utils import base64url_decode
import requests
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

class SupabaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return None

        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            raise AuthenticationFailed("Token mal formado")

        try:
            # 1️⃣ Obtener header del JWT
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header["kid"]

            # 2️⃣ Obtener JWKS desde Supabase
            jwks_url = "https://hizwrsoakyjqyhggvbuw.supabase.co/auth/v1/.well-known/jwks.json"
            jwks = requests.get(jwks_url).json()

            # 3️⃣ Buscar la key correcta
            key = next(k for k in jwks["keys"] if k["kid"] == kid)

            # 4️⃣ Decodificar token
            payload = jwt.decode(
                token,
                key,
                algorithms=["ES256"],
                audience="authenticated",
                issuer="https://hizwrsoakyjqyhggvbuw.supabase.co/auth/v1"
            )

        except Exception as e:
            raise AuthenticationFailed(f"Token inválido: {str(e)}")

        return (payload, None)