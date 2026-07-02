from django.contrib import admin

from .models import Tarea


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ["id", "titulo", "estado", "prioridad", "responsable", "created"]
    list_filter = ["estado", "prioridad"]
    search_fields = ["titulo", "descripcion"]
