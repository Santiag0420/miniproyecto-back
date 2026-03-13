from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum

from .models import SubActivity


def calcular_horas_dia(usuario, dia: date, excluir_subtarea_id=None) -> Decimal:
    """
    Suma (en DB) las horas estimadas de subtareas no completadas del usuario
    para un día específico.
    excluir_subtarea_id: evita contar doble la subtarea que se está editando.
    """
    qs = SubActivity.objects.filter(
        activity__usuario=usuario,
        fecha_objetivo=dia,
    ).exclude(estado='hecha')

    if excluir_subtarea_id is not None:
        qs = qs.exclude(pk=excluir_subtarea_id)

    resultado = qs.aggregate(total=Sum('horas_estimadas'))
    return resultado['total'] or Decimal('0')


# Alias para retrocompatibilidad con código existente que usa get_horas_dia
def get_horas_dia(usuario, dia: date, exclude_subtask_id=None) -> float:
    return float(calcular_horas_dia(usuario, dia, excluir_subtarea_id=exclude_subtask_id))


def verificar_conflicto(usuario, dia: date, horas_subtarea, excluir_subtarea_id=None) -> dict:
    """
    Verifica si una subtarea cabe en el día sin exceder el límite diario.
    horas_subtarea puede ser Decimal, float o str.
    Retorna dict con: conflict (bool), planned_hours, daily_limit, excess_hours.
    """
    limite = usuario.perfil.limite_horas_diarias
    horas_existentes = calcular_horas_dia(usuario, dia, excluir_subtarea_id)
    horas_total = horas_existentes + Decimal(str(horas_subtarea))

    return {
        'conflict': horas_total > limite,
        'planned_hours': float(horas_total),
        'daily_limit': float(limite),
        'excess_hours': float(max(horas_total - limite, Decimal('0'))),
        'existing_hours': float(horas_existentes),
    }


def generar_sugerencias(usuario, dia: date, horas_subtarea, subtarea_id=None) -> list:
    """
    Genera sugerencias tipadas (move / reduce / force) cuando hay conflicto.
    - move: próximos 7 días con espacio suficiente.
    - reduce: si quedan horas disponibles en ese día sin contar esta subtarea.
    - force: siempre presente.
    """
    limite = usuario.perfil.limite_horas_diarias
    horas_subtarea = Decimal(str(horas_subtarea))
    sugerencias = []

    # --- Sugerencia: Mover ---
    dias_disponibles = []
    for i in range(1, 8):
        dia_candidato = dia + timedelta(days=i)
        horas_dia = calcular_horas_dia(usuario, dia_candidato)
        disponible = limite - horas_dia
        if disponible >= horas_subtarea:
            dias_disponibles.append({
                'date': str(dia_candidato),
                'planned_hours': float(horas_dia),
                'available_hours': float(disponible),
            })
    if dias_disponibles:
        sugerencias.append({
            'type': 'move',
            'description': 'Mover a otro día con espacio disponible',
            'available_dates': dias_disponibles,
        })

    # --- Sugerencia: Reducir ---
    horas_sin_esta = calcular_horas_dia(usuario, dia, excluir_subtarea_id=subtarea_id)
    max_sin_conflicto = limite - horas_sin_esta
    if max_sin_conflicto > Decimal('0'):
        sugerencias.append({
            'type': 'reduce',
            'description': 'Reducir las horas estimadas de esta subtarea',
            'current_hours': float(horas_subtarea),
            'max_without_conflict': float(max_sin_conflicto),
        })

    # --- Sugerencia: Forzar (siempre) ---
    sugerencias.append({
        'type': 'force',
        'description': 'Guardar de todas formas y aceptar la sobrecarga',
    })

    return sugerencias


# Alias retrocompatibilidad (DayWorkloadView usa get_sugerencias con otros parámetros)
def get_sugerencias(usuario, horas_needed: float, limite: float, desde: date, n: int = 5) -> list:
    """
    Versión simplificada para DayWorkloadView: retorna fechas disponibles como lista plana.
    """
    sugerencias = []
    dia = desde
    intentos = 0
    while len(sugerencias) < n and intentos < 60:
        horas_ocupadas = get_horas_dia(usuario, dia)
        disponibles = limite - horas_ocupadas
        if disponibles >= horas_needed:
            sugerencias.append({
                'fecha': str(dia),
                'horas_disponibles': round(disponibles, 1),
            })
        dia += timedelta(days=1)
        intentos += 1
    return sugerencias
