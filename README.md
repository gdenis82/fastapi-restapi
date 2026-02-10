# Справочник организаций API
Тестовое задаине в файле `Тестовое задание Backend python.docx`

## Запуск локально

Настройки лежат в `.env`. Для локального запуска укажите `DATABASE_URL` с хостом `localhost`, например:

```
DATABASE_URL=postgresql+asyncpg://app:app@localhost:5432/app
```

API ключ задается через `API_KEY` и передается в заголовке `X-API-Key`.

### БД будет в докере

```bash
docker compose up -d db adminer
```
Запуск приложения fastapi (или запустите run_dev.py в режиме отладки)
```bash
uv sync
uvicorn app.main:app --reload
```

Далее миграция, наполнение тестовыми данными
```bash
uv run alembic upgrade head
uv run python -m app.seed
```


## Запуск все в Docker

Проверить путь к базе в настройках `.env`.
```
DATABASE_URL=postgresql+asyncpg://app:app@db:5432/app
```

```bash
docker compose up -d
```

Запуск сидирования внутри контейнера:

```bash
docker compose exec -T api /bin/sh -c ". /app/.venv/bin/activate && python -m app.seed"
```

## Эндпоинты и примеры

Рекомендуемый способ — использовать файл `tests/test_endpoints.http`.

Базовый URL: `http://localhost:8000`

- `GET /health` — проверка доступности

```powershell
iwr http://localhost:8000/health -Headers @{ "X-API-Key" = "changeme" }
```

- `GET /buildings` — список зданий

```powershell
iwr http://localhost:8000/buildings -Headers @{ "X-API-Key" = "changeme" }
```

- `GET /organizations/{organization_id}` — информация об организации

```powershell
iwr http://localhost:8000/organizations/1 -Headers @{ "X-API-Key" = "changeme" }
```

- `GET /organizations/by-building/{building_id}` — организации в здании

```powershell
iwr http://localhost:8000/organizations/by-building/1 -Headers @{ "X-API-Key" = "changeme" }
```

- `GET /organizations/by-activity/{activity_id}` — организации по виду деятельности

```powershell
iwr http://localhost:8000/organizations/by-activity/2 -Headers @{ "X-API-Key" = "changeme" }
```

- `GET /organizations/by-activity-tree/{activity_id}` — организации по дереву деятельности

```powershell
iwr http://localhost:8000/organizations/by-activity-tree/1 -Headers @{ "X-API-Key" = "changeme" }
```

- `GET /organizations/by-activity-name?name=&include_children=` — поиск по названию деятельности

```powershell
iwr "http://localhost:8000/organizations/by-activity-name?name=Еда&include_children=true" -Headers @{ "X-API-Key" = "changeme" }
```

- `GET /organizations/search?name=` — поиск организаций по названию

```powershell
iwr "http://localhost:8000/organizations/search?name=Авто" -Headers @{ "X-API-Key" = "changeme" }
```

- `GET /organizations/near?lat=&lon=&radius_km=` — организации в радиусе

```powershell
iwr "http://localhost:8000/organizations/near?lat=55.76&lon=37.63&radius_km=10" -Headers @{ "X-API-Key" = "changeme" }
```

- `GET /organizations/within-rect?min_lat=&max_lat=&min_lon=&max_lon=` — организации в прямоугольной области

```powershell
iwr "http://localhost:8000/organizations/within-rect?min_lat=55.7&max_lat=55.8&min_lon=37.5&max_lon=37.7" -Headers @{ "X-API-Key" = "changeme" }
```

Swagger UI доступен по `/docs`, Redoc — по `/redoc`.

## Тесты

```bash
pytest
```
