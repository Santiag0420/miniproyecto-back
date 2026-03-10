from datetime import date, timedelta

from .models import SubActivity


def get_horas_dia(user, fecha: date, exclude_subtask_id=None) -> float:
    """
    Suma las horas estimadas de subtareas no completadas del usuario en una fecha dada.
    exclude_subtask_id: excluye la subtarea que se está editando para no contarla dos veces.
    """
    qs = SubActivity.objects.filter(
        activity__usuario=user,
        fecha_objetivo=fecha,
        completada=False,
    )
    if exclude_subtask_id is not None:
        qs = qs.exclude(pk=exclude_subtask_id)
    return float(sum(s.horas_estimadas for s in qs))


def get_sugerencias(user, horas_needed: float, limite: float, desde: date, n: int = 5) -> list:
    """
    Devuelve hasta n días a partir de 'desde' donde el usuario tiene capacidad
    suficiente para agregar horas_needed horas sin superar el límite diario.
    Busca hasta 60 días hacia adelante.
    """
    sugerencias = []
    dia = desde
    intentos = 0
    while len(sugerencias) < n and intentos < 60:
        horas_ocupadas = get_horas_dia(user, dia)
        disponibles = limite - horas_ocupadas
        if disponibles >= horas_needed:
            sugerencias.append({
                'fecha': str(dia),
                'horas_disponibles': round(disponibles, 1),
            })
        dia += timedelta(days=1)
        intentos += 1
    return sugerencias
