"""
Consumer WebSocket para la vista 'Hoy'.

Flujo:
  1. El cliente conecta a ws/activities/today/?token=<JWT>
  2. Se autentica el token; si es inválido se cierra con código 4001.
  3. Se une al grupo personal del usuario (today_<user_id>).
  4. Se envían los datos actuales inmediatamente.
  5. Cada vez que el usuario crea/edita/elimina una actividad o subtarea,
     las vistas llaman a notify_today_update(user_id), que hace group_send
     al grupo, y el consumer reenvía los datos actualizados al cliente.
  6. El cliente también puede enviar cualquier mensaje para forzar un refresco.
"""

import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from .models import SubActivity
from .serializers import SubtareaHoySerializer


class TodayConsumer(AsyncWebsocketConsumer):

    # ------------------------------------------------------------------
    # Ciclo de vida de la conexión
    # ------------------------------------------------------------------

    async def connect(self):
        token_str = self._extract_token()
        self.user = await self._authenticate(token_str)

        if self.user is None:
            # Cierra sin aceptar — código 4001 = no autorizado
            await self.close(code=4001)
            return

        self.group_name = f"today_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Enviar datos actuales al conectar
        await self._push_data()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Cualquier mensaje del cliente dispara un refresco manual
        await self._push_data()

    # ------------------------------------------------------------------
    # Manejador de mensajes del canal (llamado por group_send)
    # ------------------------------------------------------------------

    async def today_update(self, event):
        """Recibe la señal del servidor y reenvía datos actualizados al cliente."""
        await self._push_data()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _push_data(self):
        data = await self._build_today_data()
        await self.send(text_data=json.dumps(data))

    def _extract_token(self):
        """Extrae el JWT del query string: ws/.../?token=<jwt>"""
        query = self.scope.get('query_string', b'').decode()
        params = {}
        for part in query.split('&'):
            if '=' in part:
                k, v = part.split('=', 1)
                params[k] = v
        return params.get('token')

    @database_sync_to_async
    def _authenticate(self, token_str):
        if not token_str:
            return None
        try:
            payload = AccessToken(token_str)
            return User.objects.get(id=payload['user_id'])
        except (InvalidToken, TokenError, User.DoesNotExist):
            return None

    @database_sync_to_async
    def _build_today_data(self):
        """Misma lógica que TodayView, ejecutada en el thread pool de Django."""
        from datetime import timedelta
        from django.db.models import Sum

        hoy = timezone.localdate()

        base_qs = SubActivity.objects.filter(
            activity__usuario=self.user,
        ).exclude(estado='hecha').select_related('activity')

        overdue = list(base_qs.filter(
            fecha_objetivo__lt=hoy
        ).order_by('fecha_objetivo', 'horas_estimadas'))

        today_qs = list(base_qs.filter(
            fecha_objetivo=hoy
        ).order_by('horas_estimadas'))

        upcoming = list(base_qs.filter(
            fecha_objetivo__gt=hoy,
            fecha_objetivo__lte=hoy + timedelta(days=7),
        ).order_by('fecha_objetivo', 'horas_estimadas'))

        return {
            'overdue':  SubtareaHoySerializer(overdue, many=True).data,
            'today':    SubtareaHoySerializer(today_qs, many=True).data,
            'upcoming': SubtareaHoySerializer(upcoming, many=True).data,
        }
