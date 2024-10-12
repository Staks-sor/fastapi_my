import uvicorn
from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.api.hotels import router as router_hotels
from src.api.rooms import router as router_rooms

app = FastAPI(docs_url=None, redoc_url=None,
              title="Мое приложение",  # Укажите название вашего API
              description="""
## Отели API

Добро пожаловать в **Отели API**.

### Возможности:
- 🔍 **Поиск по местоположению**: Ищите отели по городам или странам.
- 💲 **Фильтрация по цене**: Удобное сравнение стоимости отелей.
- ⭐ **Отзывы гостей**: Ознакомьтесь с рейтингами и отзывами, чтобы сделать лучший выбор.

---

**Автор**: Staks.
""",
              version="0.0.3",  # Укажите версию API
              openapi_url="/custom_openapi.json"  # Измените URL для OpenAPI спецификации
              )
app.include_router(router_hotels)
app.include_router(router_rooms)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
