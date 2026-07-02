"""
tareas/serializers.py
FASE 2 — Serialización Avanzada
Pipeline: data entrante -> to_internal_value() -> validate() -> .save()
HATEOAS: usamos HyperlinkedModelSerializer para que cada recurso incluya su
propia URL ('url') y así el cliente pueda navegar la API sin documentación
externa (principio "uniform interface" + "code on demand" básico).

Restricción cumplida: NO se exponen campos sensibles (notas_internas,
password, is_staff, etc). Se usa `fields` explícito, nunca '__all__'.
Validación de reglas de negocio va en el serializer (validate()), no en la vista.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Tarea

User = get_user_model()


class ResponsableSerializer(serializers.ModelSerializer):
    """Serializer anidado, solo con campos públicos del usuario."""

    class Meta:
        model = User
        fields = ["id", "username"]  # nunca password/email/is_staff aquí


class TareaSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer principal, hipervinculado (HATEOAS).
    - `url` y `responsable` son enlaces navegables generados automáticamente.
    - `dias_desde_creacion` es un campo calculado de solo lectura
      (SerializerMethodField).
    - `estado_legible` usa ReadOnlyField sobre el `get_FOO_display()` de Django.
    """

    dias_desde_creacion = serializers.SerializerMethodField()
    estado_legible = serializers.ReadOnlyField(source="get_estado_display")
    responsable_detalle = ResponsableSerializer(source="responsable", read_only=True)

    class Meta:
        model = Tarea
        fields = [
            "url",
            "id",
            "titulo",
            "descripcion",
            "estado",
            "estado_legible",
            "prioridad",
            "responsable",
            "responsable_detalle",
            "dias_desde_creacion",
            "created",
            "updated",
        ]
        read_only_fields = ["created", "updated"]
        extra_kwargs = {
            "url": {"view_name": "tarea-detail"},
            "responsable": {"view_name": "usuario-detail", "read_only": True},
        }

    def get_dias_desde_creacion(self, obj) -> int:
        from django.utils import timezone

        return (timezone.now() - obj.created).days

    # IA: drf-spectacular mostraba "unable to resolve type hint" al generar
    # el schema.yml para dias_desde_creacion.
    # Solucion manual: se anadio el type hint "-> int" al metodo
    # SerializerMethodField (drf-spectacular infiere el tipo OpenAPI desde
    # anotaciones de Python; no requiere @extend_schema_field para casos simples).

    def validate(self, data):
        """Validación anidada de reglas de negocio (no en la vista)."""
        estado = data.get("estado", getattr(self.instance, "estado", None))
        prioridad = data.get("prioridad", getattr(self.instance, "prioridad", None))

        if estado == Tarea.Estado.COMPLETADO and prioridad == Tarea.Prioridad.ALTA:
            # Regla de ejemplo: una tarea de alta prioridad no puede cerrarse
            # sin descripción de cierre.
            if not data.get("descripcion") and not getattr(self.instance, "descripcion", ""):
                raise serializers.ValidationError(
                    "Las tareas de prioridad alta requieren descripción antes de completarse."
                )
        return data

    def validate_titulo(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("El título debe tener al menos 5 caracteres.")
        return value


class TareaSerializerSimple(serializers.ModelSerializer):
    """
    Variante NO hipervinculada, útil para respuestas embebidas/anidadas
    donde no se quiere el costo de resolver reverse() en cada request.
    """

    class Meta:
        model = Tarea
        fields = ["id", "titulo", "estado", "prioridad", "created"]
        read_only_fields = fields
