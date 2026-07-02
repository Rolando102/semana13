

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

