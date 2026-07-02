"""
tareas/views.py
FASE 3 — ViewSets & Routers
FASE 4 — Filtrado, Paginación & Throttling

Mapeo HTTP <-> métodos que provee ModelViewSet automáticamente:
  GET    /tareas/          -> list
  POST   /tareas/          -> create
  GET    /tareas/{id}/     -> retrieve
  PUT    /tareas/{id}/     -> update
  PATCH  /tareas/{id}/     -> partial_update
  DELETE /tareas/{id}/     -> destroy

Vistas delgadas: no hay lógica de negocio aquí (vive en el serializer).
No se mezcla APIView con ViewSet sin justificación: todo el CRUD estándar
usa ModelViewSet; el único endpoint no estándar usa @action.
"""
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from .filters import TareaFilter
from .models import Tarea
from .serializers import TareaSerializer, ResponsableSerializer

User = get_user_model()


class CierreMasivoThrottle(UserRateThrottle):
    """
    Throttle específico y más estricto para una acción sensible/costosa.
    Se sobrescribe puntualmente (regla de la Fase 1: "sobrescribir solo
    cuando sea necesario"), el resto de acciones usa el throttle global.
    """

    scope = "cierre_masivo"


class TareaViewSet(viewsets.ModelViewSet):
    queryset = Tarea.objects.select_related("responsable").all()
    serializer_class = TareaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # FASE 4: filtrado backend (nunca en memoria)
    filterset_class = TareaFilter
    search_fields = ["titulo", "descripcion"]
    ordering_fields = ["created", "updated", "prioridad", "titulo"]
    ordering = ["-created"]  # default

    def perform_create(self, serializer):
        # Asigna automáticamente el responsable al usuario autenticado
        # (evita que el cliente falsifique el campo "responsable").
        serializer.save(responsable=self.request.user if self.request.user.is_authenticated else None)

    @action(detail=False, methods=["get"], url_path="resumen")
    def resumen(self, request):
        """
        Endpoint custom no-CRUD (GET /api/tareas/resumen/).
        Ejemplo de HATEOAS + code-on-demand mínimo: devuelve conteos y
        enlaces a los filtros relacionados.
        """
        data = {
            estado: Tarea.objects.filter(estado=estado).count()
            for estado, _ in Tarea.Estado.choices
        }
        data["_links"] = {
            estado: f"{request.build_absolute_uri('/api/tareas/')}?estado={estado}"
            for estado in data
            if estado != "_links"
        }
        return Response(data)

    @action(
        detail=False,
        methods=["post"],
        url_path="cierre-masivo",
        throttle_classes=[CierreMasivoThrottle],
    )
    def cierre_masivo(self, request):
        """
        Acción sensible: cierra todas las tareas 'activo' vencidas.
        Throttle más estricto porque es una operación de escritura masiva.
        """
        ids = request.data.get("ids", [])
        actualizadas = Tarea.objects.filter(id__in=ids, estado=Tarea.Estado.ACTIVO).update(
            estado=Tarea.Estado.COMPLETADO, updated=timezone.now()
        )
        return Response({"actualizadas": actualizadas}, status=status.HTTP_200_OK)


class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Solo lectura: necesario para que los enlaces HyperlinkedModelSerializer
    de `responsable` en TareaSerializer sean resolubles (view_name="usuario-detail").
    No expone password ni is_staff (ver ResponsableSerializer).
    """

    queryset = User.objects.all()
    serializer_class = ResponsableSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = []  # no necesita filtros/orden propios
    pagination_class = None
