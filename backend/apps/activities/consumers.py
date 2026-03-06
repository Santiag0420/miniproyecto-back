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

from .models import Activity
from .serializers import ActivitySerializer


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
        today = timezone.localdate()
        now = timezone.now()
        activities = (
            Activity.objects
            .filter(usuario=self.user)
            .prefetch_related('subactivities')
        )

        vencidas, hoy, proximas = [], [], []

        for activity in activities:
            dt_ref = activity.fecha_limite or activity.fecha_evento

            horas = sum(
                s.horas_estimadas for s in activity.subactivities.all()
                if not s.completada
            )

            fecha_local = timezone.localtime(dt_ref).date() if dt_ref else None

            data = ActivitySerializer(activity).data
            data['horas_pendientes'] = float(horas)
            data['fecha_referencia'] = str(fecha_local) if fecha_local else None

            if dt_ref is None:
                proximas.append(data)
            elif dt_ref < now:
                vencidas.append(data)
            elif fecha_local == today:
                hoy.append(data)
            else:
                proximas.append(data)

        vencidas.sort(key=lambda x: x['fecha_referencia'] or '9999-12-31')
        hoy.sort(key=lambda x: x['horas_pendientes'], reverse=True)
        proximas.sort(key=lambda x: x['fecha_referencia'] or '9999-12-31')

        return {'vencidas': vencidas, 'hoy': hoy, 'proximas': proximas}
