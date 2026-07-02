"""
tareas/models.py
Modelo de dominio para la API. `estado` y `created` llevan índice porque son
los campos de filtrado/ordering más frecuentes (Fase 4, nota técnica:
"usar índices DB para campos frecuentes").
"""
from django.conf import settings
from django.db import models


class Tarea(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        ACTIVO = "activo", "Activo"
        COMPLETADO = "completado", "Completado"
        CANCELADO = "cancelado", "Cancelado"

    class Prioridad(models.IntegerChoices):
        BAJA = 1, "Baja"
        MEDIA = 2, "Media"
        ALTA = 3, "Alta"

    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE, db_index=True
    )
    prioridad = models.IntegerField(choices=Prioridad.choices, default=Prioridad.MEDIA)
    responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tareas",
        null=True,
        blank=True,
    )
    # Campo sensible de ejemplo: NUNCA debe exponerse en el serializer.
    notas_internas = models.TextField(blank=True, help_text="Uso interno, no expuesto en la API")

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.titulo
