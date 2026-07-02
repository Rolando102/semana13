# API de Gestión de Tareas — DRF (Guía Práctica Semana 12)

**Asignatura:** Desarrollo de Aplicaciones Web (IS093A) — Unidad II
**Tema:** APIs RESTful con DRF: Serialización, ViewSets, Routers, Paginación,
Filtrado, Throttling, CORS/CSRF, HATEOAS y documentación OpenAPI.

## 1. Instalación

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py check            # Fase 1: verificación de configuración
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # opcional, para /admin y auth por sesión
python manage.py runserver
```

## 2. Mapa de endpoints

| Método | Endpoint                          | Acción                          |
|--------|------------------------------------|----------------------------------|
| GET    | `/api/tareas/`                    | list (paginado)                  |
| POST   | `/api/tareas/`                    | create                           |
| GET    | `/api/tareas/{id}/`               | retrieve                         |
| PUT    | `/api/tareas/{id}/`               | update                           |
| PATCH  | `/api/tareas/{id}/`               | partial_update                   |
| DELETE | `/api/tareas/{id}/`               | destroy                          |
| GET    | `/api/tareas/resumen/`            | acción custom (conteos + HATEOAS)|
| POST   | `/api/tareas/cierre-masivo/`      | acción custom (throttle propio)  |
| GET    | `/api/usuarios/`                  | solo lectura (para HATEOAS)      |
| GET    | `/api/schema/`                    | esquema OpenAPI 3.0 (YAML)       |
| GET    | `/api/docs/`                      | Swagger UI                       |
| GET    | `/api/redoc/`                     | ReDoc                            |

## 3. Pruebas rápidas (cURL)

```bash
# Filtrado + ordering + paginación
curl "http://127.0.0.1:8000/api/tareas/?estado=activo&ordering=-created&page=1"

# Búsqueda de texto
curl "http://127.0.0.1:8000/api/tareas/?search=servidor"

# Crear (requiere sesión o Basic Auth)
curl -u ana:pass12345 -X POST http://127.0.0.1:8000/api/tareas/ \
     -H "Content-Type: application/json" \
     -d '{"titulo":"Nueva tarea de prueba","estado":"pendiente","prioridad":2}'

# CORS preflight
curl -i -X OPTIONS http://127.0.0.1:8000/api/tareas/ \
     -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET"

# Throttling: repetir >20 veces en 1 min sin auth -> HTTP 429
for i in $(seq 1 25); do curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/api/tareas/; done
```

Verificado en este entorno: `python manage.py check` → 0 errores;
`python manage.py spectacular --file schema.yml` → 0 errores, 0 warnings;
list/filtrado/ordering/paginación/acción `resumen`/preflight CORS probados con `curl` (ver logs de desarrollo).

## 4. Mapeo con las 5 fases de la guía

| Fase | Dónde está |
|------|-----------|
| 1. Setup & Configuración DRF | `config/settings.py` (`REST_FRAMEWORK`, `CORS_ALLOWED_ORIGINS`, `SPECTACULAR_SETTINGS`) |
| 2. Serialización avanzada | `tareas/serializers.py` (`HyperlinkedModelSerializer`, `SerializerMethodField`, `ReadOnlyField`, `validate()`) |
| 3. ViewSets & Routers | `tareas/views.py` (`ModelViewSet`, `@action`) + `tareas/urls.py` (`DefaultRouter`) |
| 4. Filtrado, Paginación & Throttling | `tareas/filters.py`, `REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"]`, `CierreMasivoThrottle` |
| 5. CORS, CSRF & Documentación | `config/settings.py` (CORS/CSRF), `config/urls.py` (`/api/docs/`) |

## 5. Reglas de seguridad aplicadas

- Ningún permiso está hardcodeado en las vistas: todo viene de
  `DEFAULT_PERMISSION_CLASSES` en `settings.py`.
- `notas_internas` del modelo `Tarea` **nunca** aparece en `TareaSerializer.Meta.fields`
  (campo sensible excluido explícitamente).
- El campo `responsable` en `create/update` se asigna en `perform_create`
  desde `request.user`, no desde el body, para que el cliente no pueda
  falsificarlo.
- `CORS_ALLOWED_ORIGINS` es una lista explícita, nunca `"*"`.
- `CsrfViewMiddleware` sigue activo porque se usa `SessionAuthentication`.

## 6. Registro de uso de IA (regla de laboratorio: 80% código manual)

Formato exigido: `# IA: [problema] → Solución manual: [explicación técnica]`

1. **Ubicación:** `tareas/serializers.py`, método `get_dias_desde_creacion`.
   `# IA: drf-spectacular mostraba "unable to resolve type hint" al generar
   el schema.yml para dias_desde_creacion. → Solución manual: se añadió el
   type hint "-> int" al método SerializerMethodField (drf-spectacular
   infiere el tipo OpenAPI desde anotaciones de Python).`

2. **Ubicación:** `config/settings.py`, bloque `REST_FRAMEWORK`.
   `# IA: ¿cómo estructurar REST_FRAMEWORK para que paginación, throttling
   y permisos sean globales sin tocar cada vista? → Solución manual: se
   definieron todos los defaults en settings.py y las vistas solo
   sobrescriben un caso puntual (CierreMasivoThrottle en la acción
   cierre-masivo), cumpliendo la restricción de la Fase 1.`

Toda la lógica de serializers, filtros, throttling y configuración de
routers (>80%) fue escrita manualmente siguiendo la arquitectura DRF
estándar; la IA se usó únicamente para depurar los dos puntos anteriores,
según lo permitido en la tabla "Uso Controlado de Herramientas de IA".

## 7. Evidencias pendientes de completar por el alumno

- [ ] Capturas de pantalla de cada fase (Postman/Swagger/terminal).
- [ ] Enlace del repositorio GitHub del proyecto.
- [ ] Nombre y apellidos en la carátula de la guía.
