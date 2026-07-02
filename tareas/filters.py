"""
tareas/filters.py
FASE 4 — Filtrado avanzado
FilterSet explícito (en vez de filterset_fields como lista plana) para
soportar rangos de fecha y evitar filtrar en memoria: todo se traduce a
SQL vía QuerySet (lazy evaluation), nunca list(queryset).
"""
import django_filters

from .models import Tarea


class TareaFilter(django_filters.FilterSet):
    estado = django_filters.ChoiceFilter(choices=Tarea.Estado.choices)
    prioridad_min = django_filters.NumberFilter(field_name="prioridad", lookup_expr="gte")
    creado_despues = django_filters.DateTimeFilter(field_name="created", lookup_expr="gte")
    creado_antes = django_filters.DateTimeFilter(field_name="created", lookup_expr="lte")

    class Meta:
        model = Tarea
        fields = ["estado", "prioridad_min", "creado_despues", "creado_antes"]
