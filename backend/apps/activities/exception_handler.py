from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


_CODES = {
    400: 'VALIDATION_ERROR',
    401: 'UNAUTHORIZED',
    403: 'FORBIDDEN',
    404: 'NOT_FOUND',
    405: 'METHOD_NOT_ALLOWED',
    409: 'CONFLICT',
    500: 'INTERNAL_ERROR',
}

_MESSAGES = {
    400: 'Hay errores en los datos enviados.',
    401: 'No has iniciado sesión o tu sesión expiró.',
    403: 'No tienes permiso para esta acción.',
    404: 'El recurso no fue encontrado.',
    405: 'Método no permitido.',
    409: 'Conflicto con el estado actual del recurso.',
    500: 'Error interno del servidor.',
}


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return None

    code = _CODES.get(response.status_code, 'ERROR')
    message = _MESSAGES.get(response.status_code, 'Error desconocido.')
    fields = {}

    data = response.data
    if isinstance(data, dict):
        # Extraer campos de validación (formato DRF: {"campo": ["mensaje"]})
        for key, value in data.items():
            if key in ('detail', 'non_field_errors'):
                message = value[0] if isinstance(value, list) else str(value)
            elif isinstance(value, list) and value:
                fields[key] = value[0] if isinstance(value[0], str) else str(value[0])
            elif isinstance(value, str):
                fields[key] = value
    elif isinstance(data, list) and data:
        message = str(data[0])

    response.data = {
        'error': {
            'code': code,
            'message': message,
            'fields': fields,
        }
    }

    return response
