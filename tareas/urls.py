"""
tareas/urls.py
FASE 3 — Router
DefaultRouter genera automáticamente todas las rutas CRUD + las @action
personalizadas (resumen, cierre-masivo), manteniendo el principio DRY.
Se usa DefaultRouter (no SimpleRouter) porque queremos la vista raíz
navegable de la API (otro punto de HATEOAS).
"""
from rest_framework.routers import DefaultRouter

from .views import TareaViewSet, UsuarioViewSet

router = DefaultRouter()
router.register(r"tareas", TareaViewSet, basename="tarea")
router.register(r"usuarios", UsuarioViewSet, basename="usuario")

urlpatterns = router.urls
